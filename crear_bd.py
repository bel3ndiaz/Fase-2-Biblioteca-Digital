import os
import sqlite3

RUTA_BD = os.environ.get(
    "BIBLIOTECA_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "biblioteca.db"),
)

# (codigo, titulo, area, version, version_vigente, enlace_video, fecha_actualizacion)
INSTRUCCIONES = [
    ("IM-OFF-001", "Preparación de máquina offset", "Impresión Offset", 3, 3,
     "https://intranet.ejemplo.com/videos/offset-preparacion", "2026-09-02"),
    ("IM-OFF-002", "Cambio de planchas", "Impresión Offset", 2, 3,
     "https://intranet.ejemplo.com/videos/cambio-planchas", "2026-07-15"),
    ("IM-TIN-001", "Preparación de tinta Pantone", "Preparación de Tintas", 4, 4,
     "", "2026-09-10"),
    ("IM-TRO-001", "Ajuste de troquel", "Troquelado", 1, 2,
     "https://intranet.ejemplo.com/videos/ajuste-troquel", "2026-05-20"),
    ("IM-ACA-001", "Laminado brillante", "Acabados", 2, 2,
     "", "2026-08-01"),
    ("IM-ENC-001", "Encuadernado hot melt", "Encuadernación", 1, 3,
     "https://intranet.ejemplo.com/videos/hot-melt", "2026-04-11"),
    ("IM-MAN-001", "Calibración de cortadora", "Mantenimiento", 5, 5,
     "", "2026-09-25"),
    ("IM-CAL-001", "Inspección de calidad de impresión", "Control de Calidad", 2, 2,
     "https://intranet.ejemplo.com/videos/inspeccion-calidad", "2026-08-18"),
]


