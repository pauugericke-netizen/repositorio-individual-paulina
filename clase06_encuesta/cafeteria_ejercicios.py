# =============================================================================
# Clase 6  Encuesta a clientes de la cafetería: carga y perfilado

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


# 1. Definir la ruta donde se encuentra el archivo (relativa al repo, no a mi compu)
BASE_DIR = raiz_proyecto() / "datos"

# 2. Nombre del archivo
archivo = "Ejercicio intro - Hoja 2.csv"

# 3. Construir la ruta completa
ruta_csv = BASE_DIR / archivo

# 4. Verificar que el archivo existe
if not ruta_csv.exists():
    raise FileNotFoundError(f"No se encontró el archivo en: {ruta_csv}")

# 5. Cargar el archivo CSV
df = pd.read_csv(ruta_csv)

# 6. Inspección inicial de los datos
print(f"--- Archivo cargado exitosamente desde: {ruta_csv.name} ---")
print(df.info())

print("\nPrimeras 5 filas:")
print(df.head())


# %%
# 5.1. Dimensiones y estructura de los datos

print("\n--- Información del DataFrame ---")
df.info()

# Dimensiones: filas y columnas
print("\nDimensiones del dataset:")
print(df.shape)


# %%
# 5.2. Filas únicas: detectando la columna ID

print("\nCantidad de IDs únicos:")
print(df["id"].nunique())

# Comprobar si el ID es único
print("\n¿El ID es único?")
print(df["id"].nunique() == len(df))

# Valores únicos por columna
print("\nValores únicos por columna:")
print(df.nunique())


# %%
# 5.3. Datos faltantes

print("\n--- Datos faltantes (NA) por columna ---")
print(df.isnull().sum())

print("\n--- Cadenas vacías por columna ---")
print((df == "").sum())


# %%
# 5.4. Duplicados

print("\n--- Duplicados ---")
print(f"Cantidad de filas duplicadas: {df.duplicated().sum()}")


# %%
# 5.5. Primeras filas

print("\n--- Primeras 5 filas ---")
print(df.head())


# %%
# 6. Tipos según el libro de códigos
# El orden de las categorías no está en el archivo: se declara en el código.

orden_frecuencia = ["Nunca", "1 a 3 veces", "4 a 8 veces", "Más de 8 veces"]

if "frecuencia" in df.columns:
    df["frecuencia"] = pd.Categorical(df["frecuencia"],
                                      categories=orden_frecuencia, ordered=True)
    print("\nFrecuencia de compra:")
    print(df["frecuencia"].value_counts(sort=False))

if "atencion" in df.columns:
    df["atencion"] = pd.Categorical(df["atencion"],
                                    categories=[1, 2, 3, 4, 5], ordered=True)

# %%
# 7. Faltantes por diseño vs no respuesta
# Quien respondió "Nunca" saltó a P5: sus prod_*, atencion y pago_* deben ser NA.
# Si alguno de ellos tiene dato, hay un error de carga o de filtro.

cols_filtradas = [c for c in df.columns
                  if c.startswith(("prod_", "pago_")) or c == "atencion"]

if "frecuencia" in df.columns and cols_filtradas:
    nunca = df["frecuencia"] == "Nunca"
    errores_filtro = df.loc[nunca, cols_filtradas].notna().any(axis=1).sum()
    print("\nPersonas que respondieron 'Nunca':", int(nunca.sum()))
    print("De ellas, con datos que deberían estar vacíos:", int(errores_filtro))

    print("\nNA entre quienes SÍ compraron (no respuesta real):")
    print(df.loc[~nunca, cols_filtradas].isna().sum())

