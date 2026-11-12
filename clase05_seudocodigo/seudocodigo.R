#arranqué a hacer los códigos en R, al final me cambié a Python por el trabajo final así lo hacía con mis compañeras en visual, entonces me quedaron ambos códigos

library(here)
library(readr)

# -----------------------------------------------------------------------------
# Ejercicio 1 — Ingesta con control de codificación
# -----------------------------------------------------------------------------
ingesta_datos <- function(nombre_archivo) {
  ruta <- here("datos", nombre_archivo)
  if (!file.exists(ruta)) {
    cat("[ERROR] No se encontró el archivo:", ruta, "\n")
    return(NULL)
  }
  cat("Lectura de CSV...\n")
  df_raw <- tryCatch(
    read_csv(ruta, locale = locale(encoding = "UTF-8"), show_col_types = FALSE),
    error = function(e) {
      cat("[AVISO]: Error UTF-8, reintentando con latin-1...\n")
      read_csv(ruta, locale = locale(encoding = "latin1"), show_col_types = FALSE)
    }
  )
  cat(nrow(df_raw), "filas y", ncol(df_raw), "columnas\n")
  df_raw
}

df <- ingesta_datos("transito_aire_junio2024.csv")

# -----------------------------------------------------------------------------
# Ejercicio 2 — Filtrar temperaturas mayores a 20
# -----------------------------------------------------------------------------
temperaturas <- c(18, 22, 15, 25, 30)

# Versión 1: bucle, igual al seudocódigo
vector_filtrado <- c()
for (temp in temperaturas) {
  if (temp > 20) {
    vector_filtrado <- c(vector_filtrado, temp)
  }
}
print(vector_filtrado)              # 22 25 30

# Versión 2: vectorizada (la forma natural en R)
print(temperaturas[temperaturas > 20])

# -----------------------------------------------------------------------------
# Ejercicio 3 — Perfilado de un data frame
# -----------------------------------------------------------------------------
perfilar <- function(df) {
  cat("Filas:", nrow(df), "| Columnas:", ncol(df), "\n")
  for (columna in names(df)) {
    unicos <- length(unique(df[[columna]]))
    nulos <- sum(is.na(df[[columna]]))
    aviso <- if (unicos == nrow(df)) "  <- posible ID" else ""
    cat(columna, "| tipo:", class(df[[columna]])[1], "| únicos:", unicos,
        "| NA:", nulos, aviso, "\n")
  }
  cat("Filas duplicadas:", sum(duplicated(df)), "\n")
}

if (!is.null(df)) perfilar(df)

# -----------------------------------------------------------------------------
# Ejercicio 4 — Clasificar temperaturas
# -----------------------------------------------------------------------------
categorias <- ifelse(temperaturas < 18, "frío",
                     ifelse(temperaturas <= 25, "templado", "calor"))
print(data.frame(temperaturas, categorias))
print(table(categorias))
