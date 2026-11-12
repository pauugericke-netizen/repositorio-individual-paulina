# =============================================================================
# Clases 8 y 9 — Imagen del proyecto macro
# Evolución de la tasa de desempleo por departamento (2006-2024)
# Introducción a la Ciencia de Datos — UM, FCEE
# Paulina Gericke
# =============================================================================
# Idea del gráfico: todos los departamentos del interior en gris como
# contexto y Montevideo resaltado en rojo, para ver si la capital se mueve
# distinto al resto del país.
#
# Datos: tasa de desempleo por departamento y año (Observatorio Social, MIDES,
# en base a la ECH del INE). Guardar el CSV en datos/ con tres columnas:
#   Departamento, Año, Desempleo_%
# Si el archivo tiene otro nombre o columnas, ajustar ARCHIVO y COLUMNAS.
#
# Instalación (una sola vez):  pip install pandas matplotlib
# =============================================================================

# %%
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def raiz_proyecto() -> Path:
    """Sube carpetas hasta encontrar .git (equivalente a here::here() de R)."""
    actual = Path.cwd().resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists():
            return carpeta
    return actual


RAIZ = raiz_proyecto()
ARCHIVO = RAIZ / "datos" / "desempleo_departamentos.csv"
OUT_FIG_DIR = RAIZ / "figuras"
OUT_FIG_DIR.mkdir(exist_ok=True)

MONTEVIDEO = "Montevideo"
COLUMNAS = {"Departamento": "Departamento", "Año": "Año", "Desempleo_%": "Desempleo_%"}

# %%
# 1. Carga y preparación
if not ARCHIVO.exists():
    raise FileNotFoundError(f"No se encontró el archivo en: {ARCHIVO}")

try:
    desempleo = pd.read_csv(ARCHIVO, encoding="utf-8")
except UnicodeDecodeError:
    desempleo = pd.read_csv(ARCHIVO, encoding="latin-1")

desempleo = desempleo.rename(columns={v: k for k, v in COLUMNAS.items()})

# Tipos: año entero, desempleo numérico (acepta coma decimal)
desempleo["Año"] = pd.to_numeric(desempleo["Año"], errors="coerce").astype("Int64")
desempleo["Desempleo_%"] = pd.to_numeric(
    desempleo["Desempleo_%"].astype(str).str.replace(",", ".", regex=False),
    errors="coerce")
desempleo["Departamento"] = desempleo["Departamento"].str.strip()
desempleo = desempleo.dropna(subset=["Año", "Desempleo_%"])

# 2. Perfilado rápido
print("Dimensiones:", desempleo.shape)
print("Departamentos:", desempleo["Departamento"].nunique())
print("Años:", desempleo["Año"].min(), "a", desempleo["Año"].max())
print("¿Departamento + Año es único?",
      not desempleo.duplicated(subset=["Departamento", "Año"]).any())

# %%
# 3. Gráfico
print("\nGenerando gráficos en ./figuras/ ...")  

# Gráfica de evolución del desempleo por departamento, destacando Montevideo
fig, ax = plt.subplots(figsize=(10, 6))  # creamos la figura y definimos su tamaño

# Recorre cada departamento y ordena sus datos cronológicamente
for depto, g in desempleo.sort_values("Año").groupby("Departamento"):
    if depto == MONTEVIDEO:
        continue  # saltea Montevideo para graficarlo por separado

    # ahora graficar cada departamento del interior en gris
    ax.plot(g["Año"], g["Desempleo_%"], color="lightgray", linewidth=1, alpha=0.7)

# selecciona y ordena los datos correspondientes a Montevideo
g_mvd = desempleo[desempleo["Departamento"] == MONTEVIDEO].sort_values("Año")

# grafica Montevideo en rojo
ax.plot(g_mvd["Año"], g_mvd["Desempleo_%"], color="crimson", linewidth=2.5,
        label="Montevideo")

# agregamos títulos y qué representa cada color
ax.set_title("Evolución de la tasa de desempleo por departamento (2006-2024)\n"
             "(gris = interior, rojo = Montevideo)")

ax.set_xlabel("Año")  # Nombre del eje X.
ax.set_ylabel("Desempleo (%)")  # nombre del eje y
ax.legend()  # muestra la leyenda
fig.tight_layout()  

# Guarda el gráfico como archivo PNG en la carpeta de figuras
fig.savefig(OUT_FIG_DIR / "01_desempleo_evolucion.png")

plt.show()  # muestra el gráfico
plt.close(fig)


# %%
# 4. Lectura del gráfico
# - El gris da el rango del interior; el rojo permite comparar Montevideo
#   contra ese rango sin tener 19 colores en la leyenda.
# - Un solo color resaltado: el ojo va directo a la serie que importa.
# - Título con período y fuente de los colores; ejes con unidades.
