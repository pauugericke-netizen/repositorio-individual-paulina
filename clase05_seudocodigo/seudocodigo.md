# Clase 5 — Seudocódigo

El seudocódigo describe la lógica de un programa (qué pasos, en qué orden, qué
hacer si algo falla) antes de escribirlo en un lenguaje concreto. Cada
ejercicio de esta carpeta tiene primero el seudocódigo y después su traducción
a Python (`seudocodigo.py`) y a R (`seudocodigo.R`).

## Ejercicio 1 — Ingesta con control de codificación

```text
INICIO Ingesta_Datos
    DEFINIR ruta = raíz del proyecto / "datos" / nombre_archivo
    SI NO EXISTE ruta ENTONCES
        IMPRIMIR "[ERROR] No se encontró el archivo"
        TERMINAR
    FIN SI
    IMPRIMIR "Lectura de CSV..."
    INTENTAR
        Cargar CSV en 'df_raw' (UTF-8)
    SI FALLA POR CODIFICACIÓN ENTONCES
        IMPRIMIR "[AVISO]: Error UTF-8, reintentando con latin-1..."
        Cargar CSV en 'df_raw' (latin-1)
    FIN INTENTAR
    IMPRIMIR filas y columnas de 'df_raw'
FIN Ingesta_Datos
```

## Ejercicio 2 — Filtrar temperaturas

```text
INICIO Filtrar_Temperaturas
    DEFINIR temperaturas = [18, 22, 15, 25, 30]
    CREAR vector_filtrado VACÍO
    PARA CADA temp EN temperaturas
        SI temp > 20 ENTONCES
            AGREGAR temp A vector_filtrado
        FIN SI
    FIN PARA
    IMPRIMIR vector_filtrado          // 22 25 30
FIN Filtrar_Temperaturas
```

## Ejercicio 3 — Perfilado de un DataFrame

```text
INICIO Perfilar(df)
    IMPRIMIR cantidad de filas y columnas
    PARA CADA columna EN df
        IMPRIMIR tipo, cantidad de valores únicos, cantidad de NA
        SI valores únicos = cantidad de filas ENTONCES
            IMPRIMIR "posible ID"
        FIN SI
    FIN PARA
    IMPRIMIR cantidad de filas duplicadas
FIN Perfilar
```

## Ejercicio 4 — Clasificar temperaturas

```text
INICIO Clasificar_Temperaturas
    PARA CADA temp EN temperaturas
        SI temp < 18 ENTONCES categoría = "frío"
        SI NO, SI temp <= 25 ENTONCES categoría = "templado"
        SI NO categoría = "calor"
        IMPRIMIR temp, categoría
    FIN PARA
    CONTAR cuántas hay de cada categoría
FIN Clasificar_Temperaturas
```

## Para recordar

- El seudocódigo no depende del lenguaje: el mismo plan sale en Python y en R.
- En R el filtro se hace en una línea (`x[x > 20]`) porque las operaciones son
  vectorizadas; en Python con listas se usa un bucle o una *list comprehension*.
- Pensar primero qué puede fallar (archivo inexistente, codificación) evita
  errores difíciles de leer después.
