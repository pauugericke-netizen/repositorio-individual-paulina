# =============================================================================
# Clase 7 — Carga de datos y rutas
# Ejemplo: calidad del aire en Montevideo (ozono, PM2.5) y conteo vehicular
# Introducción a la Ciencia de Datos — UM, FCEE
# Paulina Gericke
# =============================================================================
# Datos (Intendencia de Montevideo, catálogo de datos abiertos), en datos/:
#   o3_01_2024_04_2024.csv         ozono, datos minutales por estación
#   pm_2_5_01_2024_04_2024.csv     material particulado < 2,5 micras
#   autoscope_04_2024_volumen.csv  conteo vehicular del Centro de Gestión de Movilidad
#
# Instalación (una sola vez):  pip install pandas matplotlib
# =============================================================================

# %%
import os
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt

# =============================================================================
# 1. Rutas
# =============================================================================
# Ruta ABSOLUTA: empieza en la raíz del disco. Solo funciona en MI computadora.
#   /Users/paulina/Desktop/Introducción a la Ciencia de Datos/datos/archivo.csv
# Ruta RELATIVA: se arma desde una carpeta conocida (la raíz del proyecto).
#   datos/archivo.csv  -> funciona en cualquier computadora que clone el repo.

# Directorio de trabajo actual (equivalente a getwd() en R)
print("Directorio de trabajo:", os.getcwd())


# Raíz del proyecto: subir carpetas hasta encontrar .git (equivalente a here::here())
def raiz_proyecto() -> Path:
    actual = Path.cwd().resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists():
            return carpeta
    return actual


RAIZ = raiz_proyecto()
DATOS = RAIZ / "datos"
SALIDAS = RAIZ / "salidas"
SALIDAS.mkdir(exist_ok=True)

print("Raíz del proyecto:", RAIZ)

# El operador / de pathlib une partes de la ruta con la barra correcta
# (\ en Windows, / en Mac y Linux): no hay que escribir la barra a mano.
ARCH_O3 = DATOS / "o3_01_2024_04_2024.csv"
ARCH_PM = DATOS / "pm_2_5_01_2024_04_2024.csv"
ARCH_AUTO = DATOS / "autoscope_04_2024_volumen.csv"

# Partes de una ruta
print("Nombre:", ARCH_O3.name, "| Extensión:", ARCH_O3.suffix, "| Carpeta:", ARCH_O3.parent.name)

# Qué archivos CSV hay en datos/
print("CSV disponibles en datos/:", [p.name for p in DATOS.glob("*.csv")])

# %%
# =============================================================================
# 2. Carga con verificación y control de codificación
# =============================================================================
def cargar_csv(ruta: Path, **kwargs) -> pd.DataFrame:
    """Verifica que el archivo exista y prueba UTF-8; si falla, latin-1."""
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontró {ruta.name} en {ruta.parent}. "
            "Descargarlo del catálogo de datos abiertos y guardarlo en datos/.")
    try:
        return pd.read_csv(ruta, encoding="utf-8", **kwargs)
    except UnicodeDecodeError:
        print(f"[AVISO] {ruta.name}: error con UTF-8, se carga con latin-1")
        return pd.read_csv(ruta, encoding="latin-1", **kwargs)


# pandas no reconoce fechas solo: hay que indicarlo con parse_dates
ozono = cargar_csv(ARCH_O3, parse_dates=["fecha"])
pm = cargar_csv(ARCH_PM, parse_dates=["fecha"])
auto = cargar_csv(ARCH_AUTO, parse_dates=["fecha"])

# %%
# =============================================================================
# 3. Perfilado: estructura, identificador, nulos y duplicados
# =============================================================================
for nombre, df in {"ozono": ozono, "pm2.5": pm, "autos": auto}.items():
    print(f"\n===== {nombre} =====")
    print("Dimensiones:", df.shape)
    print(df.dtypes)
    print("Nulos por columna:\n", df.isna().sum())
    print("Filas duplicadas:", df.duplicated().sum())

# Identificador: cada medición es una estación en un momento.
# ¿La combinación fecha + estación es única?
print("\n¿fecha + estación identifica cada fila de ozono?",
      not ozono.duplicated(subset=["fecha", "estacion"]).any())

# %%
# =============================================================================
# 4. Limpieza: nombres de estaciones mal codificados
# =============================================================================
# El archivo se guardó en UTF-8 pero se leyó como latin-1 (o al revés):
# "Ã³" aparece donde debería ir "ó". Se reemplaza con un diccionario.
print("Estaciones antes:", ozono["estacion"].unique())

pauta_limpieza = {"Ã³": "ó", "Ã±": "ñ", "Ã¡": "á", "Ã©": "é",
                  "Ã\xad": "í", "Ãº": "ú", "Ã“": "Ó", "Ã‘": "Ñ"}


def limpiar_texto(serie: pd.Series) -> pd.Series:
    for buscar, reemplazar in pauta_limpieza.items():
        serie = serie.str.replace(buscar, reemplazar, regex=False)
    return serie.str.strip()


for df in (ozono, pm):
    df["estacion"] = limpiar_texto(df["estacion"])

print("Estaciones después:", ozono["estacion"].unique())

# Quitar duplicados exactos
ozono = ozono.drop_duplicates()
pm = pm.drop_duplicates()

# %%
# =============================================================================
# 5. Transformación: de datos minutales a promedios por hora y por día
# =============================================================================
col_o3 = "o3"
ozono = ozono.dropna(subset=[col_o3])

o3_hora = (ozono.set_index("fecha")
                .groupby("estacion")[col_o3]
                .resample("h").mean()
                .reset_index())

o3_dia = (o3_hora.assign(dia=o3_hora["fecha"].dt.date)
                 .groupby(["estacion", "dia"])[col_o3]
                 .agg(media="mean", p95=lambda x: x.quantile(0.95))
                 .reset_index())
print(o3_dia.head())

# Guardar el resultado (ruta relativa, carpeta salidas/)
o3_dia.to_csv(SALIDAS / "clase07_ozono_diario.csv", index=False)

# %%
# =============================================================================
# 6. Gráfico: ozono diario por estación
# =============================================================================
fig, ax = plt.subplots(figsize=(10, 5))
for est, g in o3_dia.groupby("estacion"):
    ax.plot(pd.to_datetime(g["dia"]), g["media"], linewidth=1.2, label=est)
ax.set_title("Ozono: promedio diario por estación, Montevideo (enero–abril 2024)")
ax.set_xlabel("Fecha")
ax.set_ylabel("O3 (µg/m³)")
ax.legend(fontsize=8)
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
fig.savefig(SALIDAS / "clase07_ozono_diario.png", dpi=150)
plt.show()
