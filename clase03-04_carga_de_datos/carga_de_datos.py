# =============================================================================
# Clases 3 y 4 — Carga de datos 
# =============================================================================
# Mismo dataset que ejercicio_dataset_abierto.R: población por sexo, tramo de
# edad y departamento (INE). El archivo va en la carpeta datos/ del repo.
#
# Flujo: ruta -> verificar -> cargar -> limpiar encabezados -> tipos -> perfilado
# Instalación (una sola vez):  pip install pandas

#Realizamos el trabajo con Leticia Cárpena, ayudadas por Joselina en clase
# =============================================================================

# %%
from pathlib import Path

import pandas as pd


def raiz_proyecto() -> Path:
    """Sube carpetas hasta encontrar .git (equivalente a here::here() de R)."""
    actual = Path.cwd().resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists():
            return carpeta
    return actual


# 1. Ruta relativa a la raíz del proyecto: funciona en cualquier computadora
DATOS = raiz_proyecto() / "datos"
archivo = "2pobporsextodpto .csv"   # el nombre original trae un espacio antes de .csv
ruta_csv = DATOS / archivo

# 2. Verificar que el archivo existe antes de cargarlo
if not ruta_csv.exists():
    raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

# 3. Cargar sin encabezado (el archivo trae dos filas de títulos)
#    Si falla por codificación, reintentar con latin-1 (típico de datos abiertos)
try:
    df = pd.read_csv(ruta_csv, header=None, encoding="utf-8")
except UnicodeDecodeError:
    print("[AVISO] Error con UTF-8, reintentando con latin-1...")
    df = pd.read_csv(ruta_csv, header=None, encoding="latin-1")

print("Así llega el archivo:")
print(df.head())

# %%
# 4. Eliminar las dos filas de encabezados y poner nombres a las columnas
df = df.iloc[2:].reset_index(drop=True)

df.columns = [
    "Hombres_0_14", "Hombres_15_64", "Hombres_65_mas", "Hombres_Total", "Hombres_Total2",
    "Mujeres_0_14", "Mujeres_15_64", "Mujeres_65_mas", "Mujeres_Total", "Mujeres_Total2",
    "Total_0_14", "Total_15_64", "Total_65_mas", "Total_Total", "Total_Total2",
]

# 5. Convertir a numérico (llegan como texto porque había títulos en la columna).
#    Se sacan los puntos de miles por si el archivo los trae.
df = df.apply(lambda col: pd.to_numeric(
    col.astype(str).str.replace(".", "", regex=False).str.strip(), errors="coerce"))

# %%
# 6. Perfilado: diagnóstico antes de limpiar
print(f"--- Archivo cargado: {ruta_csv.name} ---")
print("Dimensiones (filas, columnas):", df.shape)

print("\nEstructura:")
df.info()

print("\nPrimeras filas:")
print(df.head())

# 6.1 Candidatos a ID: si una columna tiene tantos valores únicos como filas
print("\nValores únicos por columna:")
print(df.nunique())

# 6.2 Faltantes: NA y "falsos nulos" (cadenas vacías)
print("\nValores nulos (NA) por columna:")
print(df.isna().sum())
print("\nCadenas vacías por columna:")
print((df == "").sum())

# 6.3 Duplicados
print("\nFilas exactamente duplicadas:", df.duplicated().sum())

# 6.4 Chequeo de coherencia: hombres + mujeres = total en cada fila
diferencia = (df["Hombres_Total"] + df["Mujeres_Total"] - df["Total_Total"]).abs()
print("\nFilas donde Hombres + Mujeres no coincide con el Total:", int((diferencia > 0).sum()))
