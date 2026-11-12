# =============================================================================
# Clase 5 — Del seudocódigo al código (Python)
# Introducción a la Ciencia de Datos — UM, FCEE
# Paulina Gericke
# =============================================================================
# Cada bloque traduce un ejercicio de seudocodigo.md.
# Instalación (una sola vez):  pip install pandas
# =============================================================================

# %%
from pathlib import Path

import pandas as pd


def raiz_proyecto() -> Path:
    actual = Path.cwd().resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists():
            return carpeta
    return actual


# %%
# -----------------------------------------------------------------------------
# Ejercicio 1 — Ingesta con control de codificación
# -----------------------------------------------------------------------------
def ingesta_datos(nombre_archivo: str) -> pd.DataFrame | None:
    ruta = raiz_proyecto() / "datos" / nombre_archivo
    if not ruta.exists():
        print(f"[ERROR] No se encontró el archivo: {ruta}")
        return None
    print("Lectura de CSV...")
    try:
        df_raw = pd.read_csv(ruta, encoding="utf-8")
    except UnicodeDecodeError:
        print("[AVISO]: Error UTF-8, reintentando con latin-1...")
        df_raw = pd.read_csv(ruta, encoding="latin-1")
    print(f"{df_raw.shape[0]} filas y {df_raw.shape[1]} columnas")
    return df_raw


df = ingesta_datos("transito_aire_junio2024.csv")

# %%
# -----------------------------------------------------------------------------
# Ejercicio 2 — Filtrar temperaturas mayores a 20
# -----------------------------------------------------------------------------
temperaturas = [18, 22, 15, 25, 30]

# Versión 1: bucle, igual al seudocódigo
vector_filtrado = []
for temp in temperaturas:
    if temp > 20:
        vector_filtrado.append(temp)
print(vector_filtrado)          # [22, 25, 30]

# Versión 2: list comprehension (misma lógica en una línea)
print([temp for temp in temperaturas if temp > 20])


# %%
# -----------------------------------------------------------------------------
# Ejercicio 3 — Perfilado de un DataFrame
# -----------------------------------------------------------------------------
def perfilar(df: pd.DataFrame) -> None:
    print(f"Filas: {df.shape[0]} | Columnas: {df.shape[1]}")
    for columna in df.columns:
        unicos = df[columna].nunique()
        nulos = df[columna].isna().sum()
        aviso = "  <- posible ID" if unicos == len(df) else ""
        print(f"{columna:12} tipo={str(df[columna].dtype):8} únicos={unicos:5} NA={nulos:4}{aviso}")
    print("Filas duplicadas:", df.duplicated().sum())


if df is not None:
    perfilar(df)

# %%
# -----------------------------------------------------------------------------
# Ejercicio 4 — Clasificar temperaturas
# -----------------------------------------------------------------------------
categorias = []
for temp in temperaturas:
    if temp < 18:
        categoria = "frío"
    elif temp <= 25:
        categoria = "templado"
    else:
        categoria = "calor"
    categorias.append(categoria)
    print(temp, categoria)

print(pd.Series(categorias).value_counts())
