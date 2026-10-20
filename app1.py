"""
Biblioteca Digital de Instrucciones de Trabajo - Impresos Múltiples
Fase 2
"""
import os
import sqlite3
from datetime import date

from flask import (Flask, render_template, request, redirect, url_for,
                   flash, abort)

app = Flask(__name__)
app.secret
_key = "clave-solo-para-mensajes-flash"

RUTA_BD = os.environ.get(
    "BIBLIOTECA_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca.db"),
)

AREAS = [
    "Impresión Offset",
    "Impresión Digital",
    "Preparación de Tintas",
    "Troquelado",
    "Acabados",
    "Encuadernación",
    "Mantenimiento",
    "Control de Calidad",
]

def conectar():
    conexion = sqlite3.connect(RUTA_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute("PRAGMA foreign_keys = ON")
    return conexion


@app.template_filter("fecha")
def formato_fecha(texto):
    """Convierte 2026-10-15 en 15/10/2026 para mostrarla en pantalla."""
    partes = str(texto).split("-")
    if len(partes) == 3:
        return partes[2] + "/" + partes[1] + "/" + partes[0]
    return texto
def clasificar(version, version_vigente):
    """Misma regla que usa /resumen, para mostrar el estado en el listado."""
    if version == version_vigente:
        return "vigente"
    elif version < version_vigente:
        return "desactualizada"
    else:
        return "por_revisar"


def validar_versiones(version, version_vigente):
    errores = []
    if not version.isdigit() or int(version) < 1:
        errores.append("La versión debe ser un número entero mayor o igual a 1.")
    if not version_vigente.isdigit() or int(version_vigente) < 1:
        errores.append("La versión vigente debe ser un número entero mayor o igual a 1.")
    return errores


def validar_enlace(enlace):
    if enlace != "" and not (enlace.startswith("http://") or enlace.startswith("https://")):
        return ["El enlace de video debe comenzar con http:// o https:// (o dejarse vacío)."]
    return []


@app.route("/")
def inicio():
    return redirect(url_for("listar"))


@app.route("/instrucciones")
def listar():
    texto = request.args.get("q", "").strip()
    conexion = conectar()
    if texto == "":
        filas = conexion.execute(
            "SELECT * FROM instrucciones ORDER BY codigo").fetchall()
    else:
        patron = "%" + texto + "%"
        filas = conexion.execute(
            "SELECT * FROM instrucciones "
            "WHERE titulo LIKE ? OR codigo LIKE ? OR area LIKE ? ORDER BY codigo",
            (patron, patron, patron)).fetchall()
    conexion.close()

    instrucciones = []
    for fila in filas:
        estado = clasificar(fila["version"], fila["version_vigente"])
        instrucciones.append({"datos": fila, "estado": estado})
    return render_template("listado.html", instrucciones=instrucciones, q=texto)


@app.route("/instrucciones/<int:id>")
def detalle(id):
    conexion = conectar()
    fila = conexion.execute(
        "SELECT * FROM instrucciones WHERE id = ?", (id,)).fetchone()
    if fila is None:
        conexion.close()
        abort(404)
    historial = conexion.execute(
        "SELECT * FROM historial_versiones WHERE instruccion_id = ? "
        "ORDER BY version DESC", (id,)).fetchall()
    conexion.close()
    estado = clasificar(fila["version"], fila["version_vigente"])
    return render_template("detalle.html", i=fila, historial=historial, estado=estado)


@app.route("/instrucciones/nuevo", methods=["GET", "POST"])
def nuevo():
    errores = []
    if request.method == "POST":
        codigo = request.form["codigo"].strip().upper()
        titulo = request.form["titulo"].strip()
        area = request.form["area"]
        version = request.form["version"].strip()
        version_vigente = request.form["version_vigente"].strip()
        enlace = request.form["enlace_video"].strip()

        if codigo == "":
            errores.append("El código es obligatorio.")
        elif len(codigo) > 20:
            errores.append("El código no puede tener más de 20 caracteres.")
        if titulo == "":
            errores.append("El título es obligatorio.")
        elif len(titulo) > 100:
            errores.append("El título no puede tener más de 100 caracteres.")
        if area not in AREAS:
            errores.append("Selecciona un área de la lista.")
        errores = errores + validar_versiones(version, version_vigente) + validar_enlace(enlace)

        if not errores:
            hoy = date.today().isoformat()
            conexion = conectar()
            try:
                cursor = conexion.execute(
                    "INSERT INTO instrucciones "
                    "(codigo, titulo, area, version, version_vigente, enlace_video, fecha_actualizacion) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (codigo, titulo, area, int(version), int(version_vigente), enlace, hoy))
                conexion.execute(
                    "INSERT INTO historial_versiones (instruccion_id, version, fecha) "
                    "VALUES (?, ?, ?)", (cursor.lastrowid, int(version), hoy))
                conexion.commit()
            except sqlite3.IntegrityError:
                errores.append("Ya existe una instrucción con el código " + codigo + ".")
            conexion.close()
            if not errores:
                flash("Instrucción " + codigo + " registrada correctamente (versión "
                      + version + ") el " + formato_fecha(hoy) + ".")
                return redirect(url_for("listar"))

    return render_template("nuevo.html", errores=errores, datos=request.form, areas=AREAS)


@app.route("/instrucciones/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conexion = conectar()
    fila = conexion.execute(
        "SELECT * FROM instrucciones WHERE id = ?", (id,)).fetchone()
    if fila is None:
        conexion.close()
        abort(404)

    errores = []
    datos = fila  # valores que se muestran en el formulario
    if request.method == "POST":
        version = request.form["version"].strip()
        version_vigente = request.form["version_vigente"].strip()
        enlace = request.form["enlace_video"].strip()
        datos = request.form

        errores = validar_versiones(version, version_vigente) + validar_enlace(enlace)

        if not errores:
            hoy = date.today().isoformat()
            conexion.execute(
                "UPDATE instrucciones SET version = ?, version_vigente = ?, "
                "enlace_video = ?, fecha_actualizacion = ? WHERE id = ?",
                (int(version), int(version_vigente), enlace, hoy, id))
            if int(version) != fila["version"]:
                conexion.execute(
                    "INSERT INTO historial_versiones (instruccion_id, version, fecha) "
                    "VALUES (?, ?, ?)", (id, int(version), hoy))
            conexion.commit()
            conexion.close()
            flash("Instrucción " + fila["codigo"] + " actualizada correctamente (versión "
                  + version + ") el " + formato_fecha(hoy) + ".")
            return redirect(url_for("listar"))

    conexion.close()
    return render_template("editar.html", i=fila, datos=datos, errores=errores)


@app.route("/instrucciones/eliminar/<int:id>", methods=["POST"])
def eliminar(id):
    conexion = conectar()
    fila = conexion.execute(
        "SELECT codigo FROM instrucciones WHERE id = ?", (id,)).fetchone()
    if fila is None:
        conexion.close()
        abort(404)
    conexion.execute("DELETE FROM historial_versiones WHERE instruccion_id = ?", (id,))
    conexion.execute("DELETE FROM instrucciones WHERE id = ?", (id,))
    conexion.commit()
    conexion.close()
    flash("Instrucción " + fila["codigo"] + " eliminada.")
    return redirect(url_for("listar"))


@app.route("/resumen")
def resumen():
    conexion = conectar()
    filas = conexion.execute("SELECT * FROM instrucciones ORDER BY codigo").fetchall()
    conexion.close()

    # Contadores
    total_vigentes = 0
    total_desactualizadas = 0
    total_por_revisar = 0
    # Listas para mostrar cuáles instrucciones cayeron en cada clasificación
    vigentes = []
    desactualizadas = []
    por_revisar = []

    # Repetición: se recorre cada registro de la base de datos
    for fila in filas:
        # Decisión: se compara la versión del documento con la versión vigente
        if fila["version"] == fila["version_vigente"]:
            total_vigentes = total_vigentes + 1
            vigentes.append(fila)
        elif fila["version"] < fila["version_vigente"]:
            total_desactualizadas = total_desactualizadas + 1
            desactualizadas.append(fila)
        else:
            # La versión cargada es mayor que la vigente: dato inconsistente
            total_por_revisar = total_por_revisar + 1
            por_revisar.append(fila)

    return render_template(
        "resumen.html",
        total=len(filas),
        total_vigentes=total_vigentes,
        total_desactualizadas=total_desactualizadas,
        total_por_revisar=total_por_revisar,
        vigentes=vigentes,
        desactualizadas=desactualizadas,
        por_revisar=por_revisar,
    )


if __name__ == "__main__":
    app.run(debug=True)
