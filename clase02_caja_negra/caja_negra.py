# =============================================================================
# Clase 2 — La caja negra: de la medición al dataset
# Introducción a la Ciencia de Datos — UM, FCEE
# Paulina Gericke
# =============================================================================
# Dinámica: dentro de una caja cerrada (el "proceso generador de datos", DGP)
# hay objetos. Cada estudiante toca uno sin verlo y registra lo que percibe.
# Este script:
#   1. pasa esas mediciones a un DataFrame con los tipos correctos
#   2. genera datos nuevos a partir de la muestra (bootstrap y paramétrico)
#   3. compara la muestra real con los datos sintéticos
#
# Instalación (una sola vez):  pip install pandas numpy matplotlib
# =============================================================================

# %%
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def raiz_proyecto(marcadores=(".git", "README.md")) -> Path:
    """Sube carpetas hasta encontrar la raíz del repo (equivalente a here::here())."""
    actual = Path.cwd().resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists():
            return carpeta
    return actual


SALIDAS = raiz_proyecto() / "salidas"
SALIDAS.mkdir(exist_ok=True)

# %%
# -----------------------------------------------------------------------------
# 1. Registro de la dinámica: un diccionario con una lista por variable
# -----------------------------------------------------------------------------
# Tipos de variable que se registraron:
#   nominal   -> textura (suave, rugoso, poroso)
#   ordinal   -> rigidez (blando < medio < rígido)
#   discreta  -> cantidad de aristas detectadas
#   continua  -> peso estimado en gramos
#   metadato  -> certeza del observador (1 a 5)
datos_caja = {
    "objeto_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "textura": ["suave", "rugoso", "poroso", "suave", "rugoso",
                "suave", "poroso", "rugoso", "suave", "poroso"],
    "rigidez": ["blando", "rígido", "medio", "blando", "rígido",
                "rígido", "blando", "medio", "medio", "blando"],
    "num_aristas": [0, 8, 0, 4, 12, 0, 0, 6, 4, 0],
    "peso_estimado_g": [45.0, 120.5, 15.0, 85.0, 210.0, 35.0, 18.5, 95.0, 70.0, 22.0],
    "certeza_observador": [5, 4, 3, 5, 4, 2, 4, 3, 4, 3],
}

df = pd.DataFrame(datos_caja)

# Declarar los tipos: el archivo no sabe que "rigidez" tiene un orden
df["textura"] = df["textura"].astype("category")
df["rigidez"] = pd.Categorical(df["rigidez"],
                               categories=["blando", "medio", "rígido"],
                               ordered=True)

print("Estructura del DataFrame:")
df.info()
print(df.head())

# %%
# -----------------------------------------------------------------------------
# 2. Descripción rápida de la muestra real (N = 10)
# -----------------------------------------------------------------------------
print("\nFrecuencia de texturas:")
print(df["textura"].value_counts())

print("\nFrecuencia de rigidez (respeta el orden declarado):")
print(df["rigidez"].value_counts(sort=False))

print("\nResumen de variables numéricas:")
print(df[["num_aristas", "peso_estimado_g", "certeza_observador"]].describe().round(1))

# Como la rigidez es ordinal, se puede comparar con < y >
print("\nObjetos más rígidos que 'blando':")
print(df.loc[df["rigidez"] > "blando", ["objeto_id", "rigidez"]])

# %%
# -----------------------------------------------------------------------------
# 3. Datos sintéticos
# -----------------------------------------------------------------------------
rng = np.random.default_rng(42)   # semilla: mismo resultado cada vez

# Método 1: BOOTSTRAP -> muestreo con reemplazo de las filas reales (N = 100)
df_bootstrap = df.sample(n=100, replace=True, random_state=42).reset_index(drop=True)

# Método 2: PARAMÉTRICO -> suponemos que el peso sigue una Normal (N = 500)
mu = df["peso_estimado_g"].mean()
sigma = df["peso_estimado_g"].std()
pesos_sinteticos = rng.normal(loc=mu, scale=sigma, size=500)
pesos_sinteticos = np.clip(pesos_sinteticos, a_min=1.0, a_max=None)  # un peso no puede ser <= 0

print(f"\nMedia real: {mu:.1f} g | desvío real: {sigma:.1f} g")
print(f"Media bootstrap: {df_bootstrap['peso_estimado_g'].mean():.1f} g")
print(f"Media paramétrica: {pesos_sinteticos.mean():.1f} g")

# Qué pasó con los valores: el bootstrap solo repite pesos que existen;
# la Normal inventa pesos que nunca se observaron (y hasta tiene que recortar negativos).
print("Pesos distintos en bootstrap:", df_bootstrap["peso_estimado_g"].nunique())
print("Pesos sintéticos recortados a 1 g:", int((pesos_sinteticos == 1.0).sum()))

# %%
# -----------------------------------------------------------------------------
# 4. Comparación gráfica: real vs sintético
# -----------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist(pesos_sinteticos, bins=30, density=True, alpha=0.5,
        color="steelblue", label="Sintético Normal (N=500)")
ax.hist(df_bootstrap["peso_estimado_g"], bins=30, density=True, alpha=0.5,
        color="orange", label="Bootstrap (N=100)")
ax.scatter(df["peso_estimado_g"], np.zeros(len(df)), color="crimson",
           zorder=3, label="Muestra real (N=10)")
ax.set_title("Peso estimado de los objetos de la caja: real vs sintético")
ax.set_xlabel("Peso estimado (g)")
ax.set_ylabel("Densidad")
ax.legend()
for lado in ("top", "right"):
    ax.spines[lado].set_visible(False)
fig.tight_layout()
fig.savefig(SALIDAS / "clase02_real_vs_sintetico.png", dpi=150)
plt.show()

# %%
# -----------------------------------------------------------------------------
# Conclusiones
# -----------------------------------------------------------------------------
# - El modelo no sabe cómo se midió el peso (a ojo, tocando 15 segundos):
#   si la medición es mala, todo lo que se construya encima hereda el error.
# - El bootstrap respeta la forma de la muestra pero no crea valores nuevos.
# - La Normal crea valores nuevos, pero asume una sola "campana" cuando en la
#   caja hay objetos muy distintos: genera datos "fantasma" que no existen.
