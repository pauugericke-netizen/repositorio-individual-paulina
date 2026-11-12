# =============================================================================
# Clase 10 — ¿El tránsito ensucia el aire?
# Conteo vehicular, NO2 y PM2.5 por hora — Montevideo, junio de 2024
# Introducción a la Ciencia de Datos — UM, FCEE
# Paulina Gericke
# =============================================================================
# Datos: datos/transito_aire_junio2024.csv (una fila por estación y hora)
#   hora      fecha y hora (hora local, aunque el archivo la marque como UTC)
#   transito  vehículos por hora en los puntos de conteo cercanos a la estación
#   no2       dióxido de nitrógeno (µg/m³)
#   pm25      material particulado < 2,5 micras (µg/m³)
#   estacion  estación de monitoreo de calidad del aire
#
# Cada paso tiene un gráfico y al final una nota: qué vemos y qué todavía no sabemos.
# Instalación (una sola vez):  pip install pandas numpy matplotlib
# =============================================================================

# %%
from pathlib import Path

import numpy as np
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
ARCHIVO = RAIZ / "datos" / "transito_aire_junio2024.csv"
SALIDAS = RAIZ / "salidas"
SALIDAS.mkdir(exist_ok=True)


def estetica(ax):
    ax.grid(alpha=0.3)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


# %%
# =============================================================================
# 0. Carga y perfilado
# =============================================================================
if not ARCHIVO.exists():
    raise FileNotFoundError(f"No se encontró el archivo en: {ARCHIVO}")

aire = pd.read_csv(ARCHIVO, parse_dates=["hora"])

# La hora trae la marca "Z" (UTC), pero los valores ya están en hora local:
# si se convierte a UTC-3, el tránsito "empieza" a las 3 de la mañana, lo que
# no tiene sentido. Se quita la zona horaria sin mover las horas.
aire["hora"] = aire["hora"].dt.tz_localize(None)
aire["h"] = aire["hora"].dt.hour
aire["finde"] = aire["hora"].dt.dayofweek >= 5          # sábado o domingo
aire["tipo_dia"] = np.where(aire["finde"], "Fin de semana", "Entre semana")
aire["transito_miles"] = aire["transito"] / 1000

aire.info()
print("\n¿estacion + hora identifica cada fila?",
      not aire.duplicated(subset=["estacion", "hora"]).any())
print("\nHoras con dato por estación (count no cuenta los NA):")
print(aire.groupby("estacion")[["transito", "no2", "pm25"]].count())
print("\nTránsito promedio por estación (vehículos/hora):")
print(aire.groupby("estacion")["transito"].mean().round(0).sort_values(ascending=False))

# Qué vemos: el NO2 falta entero en Museo Romántico y en buena parte de
#   Tres Cruces. Tres Cruces es la estación con mucho más tránsito alrededor.
# Decisión: trabajamos con Tres Cruces, aceptando que tiene menos horas de NO2.
ESTACION = "Tres Cruces"
tc = aire[aire["estacion"] == ESTACION].set_index("hora").sort_index()

# %%
# =============================================================================
# PASO 1. Mirar las series: una semana
# =============================================================================
semana = tc.loc["2024-06-03":"2024-06-09"]

fig, axes = plt.subplots(3, 1, figsize=(11, 7), sharex=True)
for ax, col, titulo in zip(axes,
                           ["transito_miles", "no2", "pm25"],
                           ["Tránsito (miles de vehículos/h)", "NO2 (µg/m³)", "PM2.5 (µg/m³)"]):
    ax.plot(semana.index, semana[col], linewidth=1.2)
    ax.set_ylabel(titulo, fontsize=9)
    estetica(ax)
axes[0].set_title(f"{ESTACION}: una semana de junio 2024 (3 al 9)")
fig.tight_layout()
fig.savefig(SALIDAS / "clase10_paso1_semana.png", dpi=150)
plt.show()

# Qué vemos: el tránsito sube de día y baja de noche; el NO2 parece seguir
#   ese ritmo; el PM2.5 tiene picos sueltos que no se parecen al tránsito.
# Qué no sabemos: "parece" no alcanza; hay que mirar todos los días juntos.

# %%
# =============================================================================
# PASO 2. El día típico: perfil horario entre semana y fin de semana
# =============================================================================
perfil = tc.groupby(["tipo_dia", "h"])[["transito", "no2", "pm25"]].mean()

fig, axes = plt.subplots(1, 3, figsize=(13, 4))
for ax, col, titulo in zip(axes, ["transito", "no2", "pm25"],
                           ["Tránsito (veh/h)", "NO2 (µg/m³)", "PM2.5 (µg/m³)"]):
    for tipo, g in perfil[col].groupby(level="tipo_dia"):
        ax.plot(g.index.get_level_values("h"), g.values, marker="o", markersize=3, label=tipo)
    ax.set(title=titulo, xlabel="Hora del día")
    estetica(ax)
axes[0].legend()
fig.suptitle(f"{ESTACION}: perfil horario promedio, junio 2024")
fig.tight_layout()
fig.savefig(SALIDAS / "clase10_paso2_perfil_horario.png", dpi=150)
plt.show()

print("Días con NO2 por tipo de día:")
print(tc.dropna(subset=["no2"]).groupby("tipo_dia").apply(lambda d: d.index.normalize().nunique()))

# Qué vemos: el NO2 tiene picos en las mismas horas que el tránsito, más
#   marcados entre semana. El PM2.5 no sigue ese ritmo.
# Ojo: el fin de semana se apoya en pocos días con NO2.
# Qué no sabemos: dos series con ciclo diario se parecen aunque no tengan
#   relación (la luz del sol también tiene ciclo diario).

# %%
# =============================================================================
# PASO 3. Correlación "cruda" y recta
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
resumen = {}
for ax, col, titulo in zip(axes, ["no2", "pm25"], ["NO2 (µg/m³)", "PM2.5 (µg/m³)"]):
    d = tc[["transito_miles", col]].dropna()
    r = d["transito_miles"].corr(d[col])
    pendiente, ordenada = np.polyfit(d["transito_miles"], d[col], 1)
    resumen[col] = {"n_horas": len(d), "r": r, "ordenada": ordenada,
                    "pendiente": pendiente, "R2": r ** 2}
    ax.scatter(d["transito_miles"], d[col], s=8, alpha=0.4)
    x = np.linspace(d["transito_miles"].min(), d["transito_miles"].max(), 50)
    ax.plot(x, ordenada + pendiente * x, color="crimson")
    ax.set(title=f"{titulo} vs tránsito  (r = {r:.2f}, n = {len(d)})",
           xlabel="Tránsito (miles de vehículos/h)", ylabel=titulo)
    estetica(ax)
fig.tight_layout()
fig.savefig(SALIDAS / "clase10_paso3_dispersion.png", dpi=150)
plt.show()

print(pd.DataFrame(resumen).T.round(3))

# Qué vemos: el NO2 sube con el tránsito; el PM2.5 casi no.
#   La pendiente dice cuánto sube el NO2 por cada mil vehículos más por hora;
#   la ordenada es el NO2 que la recta asigna a una hora sin tránsito.
# Qué no sabemos: parte de esa r viene solo de que ambas series tienen
#   ciclo diario. ¿Cuánto queda si sacamos el ciclo?

# %%
# =============================================================================
# PASO 4. Sacar el ciclo diario: desvíos respecto de lo habitual
# =============================================================================
# A cada hora se le resta el promedio de esa hora en ese tipo de día.
# El desvío responde: ¿esta hora estuvo por encima o por debajo de lo habitual?
def desvio(s: pd.Series) -> pd.Series:
    return s - s.groupby([tc["finde"], tc["h"]]).transform("mean")


res = tc[["transito_miles", "no2", "pm25"]].apply(desvio)

for col in ["no2", "pm25"]:
    cruda = tc["transito_miles"].corr(tc[col])
    sin_ciclo = res["transito_miles"].corr(res[col])
    print(f"{col}: r cruda = {cruda:.2f} | r sin ciclo diario = {sin_ciclo:.2f}")

# %%
# =============================================================================
# PASO 5. ¿El efecto llega con retraso? Correlación con rezagos
# =============================================================================
# k > 0: contaminante de esta hora vs tránsito de k horas antes.
REZAGOS = range(-6, 13)
fig, ax = plt.subplots(figsize=(9, 4.5))
for col, nombre in [("no2", "NO2"), ("pm25", "PM2.5")]:
    c = pd.Series({k: res[col].corr(res["transito_miles"].shift(k)) for k in REZAGOS})
    ax.plot(c.index, c.values, marker="o", markersize=4, label=nombre)
    print(f"{nombre}: r máxima = {c.max():.2f} con rezago de {c.idxmax()} h")
ax.axhline(0, color="grey", linewidth=0.8)
ax.axvline(0, color="grey", linewidth=0.8, linestyle="--")
ax.set(title=f"{ESTACION}: desvíos del contaminante vs tránsito de k horas antes",
       xlabel="Rezago k (horas)", ylabel="Correlación")
ax.legend()
estetica(ax)
fig.tight_layout()
fig.savefig(SALIDAS / "clase10_paso5_rezagos.png", dpi=150)
plt.show()

# %%
# =============================================================================
# Conclusiones
# =============================================================================
# - En Tres Cruces el NO2 acompaña al tránsito, incluso después de sacar el
#   ciclo diario: es la huella del tránsito que buscábamos.
# - El PM2.5 no muestra esa relación: depende de otras fuentes (quema,
#   viento, polvo) además de los autos.
# - Límites: solo junio, una estación, NO2 con muchos huecos. Correlación no
#   es causalidad: el clima puede mover a la vez tránsito y contaminación.
