# Biblioteca Digital de Instrucciones de Trabajo: Fase 2

Reto del Socio Formador **Impresos Múltiples**. Prototipo web hecho con Python (Flask), SQLite y una hoja de estilos CSS.

## Qué hace el sistema
Centraliza las instrucciones de trabajo estandarizadas de la planta (por ejemplo, "Cambio de planchas" o "Ajuste de troquel") junto con su versión. Permite **registrar, consultar, modificar y eliminar** instrucciones, ver el historial de versiones de cada una y buscar por código, título o área.

El **resumen** recorre todas las instrucciones y las clasifica como **vigentes** o **desactualizadas** comparando la versión del documento cargado con la versión vigente (la oficial más reciente), y cuenta cuántas hay de cada tipo.

## Cómo ejecutarlo
Requiere Python 3.9 o superior. Desde la carpeta del proyecto:

```
pip install flask
python crear_bd.py
python app.py
```

Luego abrir en el navegador:

- http://127.0.0.1:5000/instrucciones (listado)
- http://127.0.0.1:5000/resumen (resumen)

`crear_bd.py` crea `biblioteca.db` con 8 instrucciones de ejemplo. Si se vuelve a ejecutar, borra los datos y empieza de cero.

## Estructura de archivos
```
fase2_equipo/
|-- app.py              # rutas de Flask, validaciones y lógica del sistema
|-- crear_bd.py         # crea las tablas y carga 8 instrucciones de ejemplo
|-- requirements.txt    # dependencias (flask)
|-- README.md           # esta documentación
|-- templates/
|   |-- base.html       # encabezado, navegación y enlace a style.css (lo heredan todas las páginas)
|   |-- listado.html    # tabla de instrucciones, búsqueda, botones modificar y eliminar
|   |-- nuevo.html      # formulario de registro
|   |-- editar.html     # formulario de modificación
|   |-- detalle.html    # datos de una instrucción e historial de versiones
|   |-- resumen.html    # contadores y listas por clasificación
|-- static/
|   |-- style.css       # única hoja de estilos del sitio
```

## Rutas
| Ruta | Método | Qué hace |
|---|---|---|
| `/` | GET | Redirige a `/instrucciones` |
| `/instrucciones` | GET | **Consultar:** lista las instrucciones con su versión y estado. Acepta `?q=texto` para buscar |
| `/instrucciones/<id>` | GET | Detalle de una instrucción y su historial de versiones |
| `/instrucciones/nuevo` | GET, POST | **Registrar:** GET muestra el formulario, POST valida y guarda |
| `/instrucciones/editar/<id>` | GET, POST | **Modificar:** GET muestra el formulario, POST valida y actualiza la versión |
| `/instrucciones/eliminar/<id>` | POST | **Eliminar:** el botón del listado pide confirmación antes de enviar |
| `/resumen` | GET | Recorre todos los registros, los clasifica y muestra los contadores |

Todas las sentencias SQL usan parámetros `?`; nunca se concatena texto escrito por el usuario.

## Base de datos (SQLite, archivo `biblioteca.db`)
**Tabla `instrucciones`**

| Campo | Tipo | Descripción |
|---|---|---|
| id | entero (clave primaria) | Identificador automático |
| codigo | texto, único | Código de la instrucción (ej. IM-OFF-001) |
| titulo | texto | Nombre de la instrucción |
| area | texto | Área de la planta |
| version | entero | Versión del documento cargado en la biblioteca |
| version_vigente | entero | Última versión oficial aprobada |
| enlace_video | texto (opcional) | URL a un video en el repositorio interno |
| fecha_actualizacion | texto (AAAA-MM-DD) | Fecha del último cambio |

**Tabla `historial_versiones`**

| Campo | Tipo | Descripción |
|---|---|---|
| id | entero (clave primaria) | Identificador automático |
| instruccion_id | entero (clave foránea → instrucciones.id) | Instrucción a la que pertenece |
| version | entero | Número de versión registrada |
| fecha | texto (AAAA-MM-DD) | Fecha en que se registró esa versión |

## Validaciones de los formularios
- Código y título obligatorios (máximo 20 y 100 caracteres); el código no puede repetirse.
- El área debe ser una de la lista.
- Versión y versión vigente deben ser enteros mayores o iguales a 1.
- El enlace de video es opcional; si se escribe debe empezar con `http://` o `https://`.
- Al registrar o modificar se guarda la fecha del cambio (campo `fecha_actualizacion` y tabla `historial_versiones`); se muestra en el listado (columna "Actualizada"), en el detalle, en el formulario de modificación y en el mensaje de confirmación (formato DD/MM/AAAA).
- Si hay un error se muestra el mensaje, no se guarda nada y el formulario conserva lo escrito. Al guardar correctamente se redirige al listado.

## Cómo funciona el resumen
La ruta `/resumen` lee todas las filas de `instrucciones` y las recorre con un `for`. En cada vuelta decide con `if / elif / else`:

1. `version == version_vigente` → **vigente** (verde)
2. `version < version_vigente` → **desactualizada** (rojo)
3. en cualquier otro caso (`version > version_vigente`, dato inconsistente) → **por revisar** (amarillo)

Un contador por clasificación se incrementa en cada vuelta, y el resultado se muestra en pantalla con una tarjeta de color distinto por clasificación, junto con la lista de instrucciones de cada grupo.

## Equipo: parte de código desarrollada por cada integrante
- José Daniel Gregg (jdanielgregg):** conexión a la base de datos, `crear_bd.py`, funciones de apoyo (`clasificar`, validaciones), registro con validación (`/instrucciones/nuevo`), `base.html` y `nuevo.html`.
- María Belén Díaz 2 (bel3ndiaz):** consulta (listado, búsqueda y detalle), eliminación con confirmación, `listado.html`, `detalle.html` y la hoja de estilos `style.css`.
- Horacio Larios (A-858):** modificación con validación e historial de versiones (`/instrucciones/editar/<id>`), resumen con repetición y decisión (`/resumen`), `editar.html` y `resumen.html` y registro de pruebas.
