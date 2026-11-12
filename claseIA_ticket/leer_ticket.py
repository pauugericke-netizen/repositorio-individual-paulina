

# %%
import base64
from pathlib import Path

import pandas as pd
import requests


def raiz_proyecto() -> Path:
    """Sube carpetas hasta encontrar .git (equivalente a here::here() de R)."""
    actual = Path.cwd().resolve()
    for carpeta in [actual, *actual.parents]:
        if (carpeta / ".git").exists():
            return carpeta
    return actual


# ---------------------------------------------------------------------
# 1. Datos de la solicitud
# ---------------------------------------------------------------------
CARPETA = raiz_proyecto() / "claseIA_ticket"
ARCH_CLAVE = CARPETA / "clave_gemini.txt"
FOTO = CARPETA / "ticket.jpg"
TIPO = "image/jpeg"                 # si la foto es .png, poner "image/png"
MODELO = "gemini-3.5-flash-lite"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"

if not ARCH_CLAVE.exists():
    raise SystemExit(f"Falta la clave: crear {ARCH_CLAVE.name} en {CARPETA}")
CLAVE = ARCH_CLAVE.read_text().strip()

INSTRUCCION = """Transcribí los ítems de este ticket de compra.
Respondé solo con una tabla CSV, sin ningún otro texto, con dos columnas:
descripcion,monto
- monto con punto decimal y sin separador de miles (1.250,00 se escribe 1250.00)
- no incluyas SUBTOTAL, IVA, TOTAL, EFECTIVO, CAMBIO ni TARJETA
- si algo no se puede leer, dejalo vacío; no lo inventes"""

# %%
# ---------------------------------------------------------------------
# 2. Pasar la foto a base64 (texto), porque el JSON solo admite texto
# ---------------------------------------------------------------------
bytes_foto = FOTO.read_bytes()
imagen_base64 = base64.b64encode(bytes_foto).decode("ascii")

print("La foto pesa", len(bytes_foto), "bytes")
print("En base64 son", len(imagen_base64), "caracteres")

# ---------------------------------------------------------------------
# 3. Armar el cuerpo de la solicitud (diccionario que se envía como JSON)
# ---------------------------------------------------------------------
cuerpo = {
    "contents": [{
        "parts": [
            {"text": INSTRUCCION},
            {"inline_data": {"mime_type": TIPO, "data": imagen_base64}},
        ]
    }],
    "generationConfig": {"temperature": 0},   # 0 = la respuesta más estable posible
}

# %%
# ---------------------------------------------------------------------
# 4. Enviar la solicitud: método POST, con la clave en un encabezado
# ---------------------------------------------------------------------
respuesta = requests.post(URL, headers={"x-goog-api-key": CLAVE}, json=cuerpo, timeout=120)

print("Código de estado:", respuesta.status_code)   # 200 = todo bien
if respuesta.status_code != 200:
    print(respuesta.text)                          # mensaje de error del servidor
    raise SystemExit("La solicitud falló: revisar el código de estado")

# ---------------------------------------------------------------------
# 5. Leer la respuesta
# ---------------------------------------------------------------------
datos = respuesta.json()                                  # JSON -> diccionario
texto = datos["candidates"][0]["content"]["parts"][0]["text"]
print(texto)

uso = datos.get("usageMetadata", {})
print("Tokens de entrada (imagen + instrucción):", uso.get("promptTokenCount"))
print("Tokens de salida (la respuesta):", uso.get("candidatesTokenCount"))

# %%
# ---------------------------------------------------------------------
# 6. Guardar la tabla y abrirla con pandas
# ---------------------------------------------------------------------
texto = texto.replace("```csv", "").replace("```", "").strip()   # por si la envuelve
salida = CARPETA / "ticket_gemini.csv"
salida.write_text(texto + "\n", encoding="utf-8")

tabla = pd.read_csv(salida)
tabla["monto"] = pd.to_numeric(tabla["monto"], errors="coerce")
print(tabla)

# ---------------------------------------------------------------------
# 7. Control de calidad: la IA puede equivocarse
# ---------------------------------------------------------------------
print("Ítems leídos:", len(tabla))
print("Montos que no se pudieron leer:", tabla["monto"].isna().sum())
print("Suma de los ítems:", round(tabla["monto"].sum(), 2))
# Comparar esta suma con el TOTAL impreso en el ticket. Si no coincide,
# la transcripción tiene errores: revisar a mano antes de usar los datos.
