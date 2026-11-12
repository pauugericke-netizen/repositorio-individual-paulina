# Clase 6  Diseño de encuestas

## Ejercicio: de la tabla al cuestionario

Se quiere obtener esta tabla a partir de una encuesta a clientes de la
cafetería de la facultad. Primero se diseña la tabla (libro de códigos) y
después el cuestionario que la produce.

### Libro de códigos

| Variable | Tipo | Valores | Faltante |
|---|---|---|---|
| `id` | entero | 1, 2, … | no admite |
| `frecuencia` | ordinal | Nunca < 1 a 3 veces < 4 a 8 veces < Más de 8 veces | NA |
| `prod_cafe`, `prod_comida`, `prod_frias`, `prod_otros` | binaria (×4) | 0, 1 | NA si `frecuencia` = Nunca |
| `atencion` | ordinal | 1 < 2 < 3 < 4 < 5 | NA si `frecuencia` = Nunca |
| `pago_efectivo`, `pago_tarjeta`, `pago_transferencia` | binaria (×3) | 0, 1 | NA si `frecuencia` = Nunca |
| `estudiante` | binaria | TRUE, FALSE | NA |
| `edad` | cuantitativa | años | NA |
| `mejora` | texto | libre | vacío |

### Cuestionario

**P1.** En los **últimos 30 días**, ¿con qué frecuencia compró en la cafetería de la facultad?
☐ Nunca → *pasar a P5* ☐ 1 a 3 veces ☐ 4 a 8 veces ☐ Más de 8 veces
→ `frecuencia`

**P2.** En los últimos 30 días, ¿qué productos compró en la cafetería? *(marque todas las que correspondan)*
☐ Café ☐ Comida ☐ Bebidas frías ☐ Otros
→ `prod_cafe`, `prod_comida`, `prod_frias`, `prod_otros` (1 si marcó, 0 si no)

**P3.** En los últimos 30 días, ¿cómo calificaría la atención recibida?
1 = Muy mala · 2 · 3 · 4 · 5 = Muy buena
→ `atencion`

**P4.** En los últimos 30 días, ¿con qué medios pagó en la cafetería? *(marque todas las que correspondan)*
☐ Efectivo ☐ Tarjeta ☐ Transferencia
→ `pago_efectivo`, `pago_tarjeta`, `pago_transferencia`

**P5.** ¿Es estudiante de esta facultad?
☐ Sí ☐ No
→ `estudiante`

**P6.** ¿Qué mejoraría del servicio de la cafetería? ______________________
→ `mejora`

**P7.** ¿Cuántos años cumplidos tiene? ____
→ `edad`

`id` no se pregunta: lo asigna quien carga los datos.

### Verificación

- Todas las preguntas sobre el consumo tienen período de referencia (últimos 30 días).
- Hay un filtro después de `frecuencia`: quien responde "Nunca" salta a P5, y
  por eso sus `prod_*`, `atencion` y `pago_*` quedan vacíos **por diseño**
  (no es no respuesta).
- `prod_*` y `pago_*` salen de preguntas de **selección múltiple**: una
  columna binaria por opción, no una opción "ambos".
- `atencion` tiene los dos extremos etiquetados y va de negativo a positivo.
- La edad va al final (dato personal: se pregunta cuando ya hay confianza).
- **7 preguntas producen 13 columnas** (más el `id`).

## Para la bitácora: seis preguntas con problemas

| # | Pregunta original | Problema | Reescritura | Variable que produce |
|---|---|---|---|---|
| 1 | ¿Está conforme con lo que gasta en comida y en transporte? | **Doble cañón**: pregunta dos cosas a la vez; si está conforme con una y no con la otra, no puede responder. | Dos preguntas: "¿Qué tan conforme está con lo que gasta en comida?" y "…en transporte?" (1 = Nada conforme … 5 = Muy conforme) | 2 columnas ordinales |
| 2 | ¿No le parece que gasta demasiado en salidas? | **Inducida y con negación**: sugiere la respuesta y confunde al responder "sí/no". | "En los últimos 30 días, ¿cuánto gastó en salidas? $____" | 1 cuantitativa (u ordinal si se usan tramos) |
| 3 | ¿Cuánto gastó últimamente en ropa? | **Sin período de referencia**: "últimamente" significa algo distinto para cada persona. | "En los últimos 30 días, ¿cuánto gastó en ropa? $____" | 1 cuantitativa |
| 4 | Gasto en transporte: ☐ $0 a $1.000 ☐ $1.000 a $3.000 ☐ $3.000 a $6.000 | Tramos **no excluyentes** (1.000 y 3.000 están en dos tramos) y **no exhaustivos** (falta más de 6.000); además no tiene período. | "En los últimos 30 días, su gasto en transporte fue: ☐ Nada ☐ Hasta $1.000 ☐ $1.001 a $3.000 ☐ $3.001 a $6.000 ☐ Más de $6.000" | 1 ordinal |
| 5 | ¿Cómo paga sus gastos? ☐ Efectivo ☐ Tarjeta ☐ Ambos ☐ Transferencia | **Selección múltiple disfrazada**: "Ambos" no dice cuáles, y no contempla combinaciones con transferencia. | "¿Con qué medios pagó sus gastos en los últimos 30 días? (marque todas) ☐ Efectivo ☐ Tarjeta ☐ Transferencia" | 3 binarias (`pago_efectivo`, `pago_tarjeta`, `pago_transferencia`) |
| 6 | (Primera pregunta) ¿Cuál es el ingreso mensual exacto de su hogar? | **Pregunta sensible al inicio** y con **precisión innecesaria**: aumenta el abandono y la no respuesta. | Moverla al final y ofrecer tramos: "El ingreso mensual de su hogar está entre: ☐ Hasta $30.000 ☐ $30.001 a $60.000 ☐ $60.001 a $100.000 ☐ Más de $100.000 ☐ Prefiero no responder" | 1 ordinal |

## Carga y perfilado

`cafeteria_ejercicios.py` carga las respuestas (CSV en `datos/`), revisa
dimensiones, ID, faltantes y duplicados, declara el orden de `frecuencia` y
`atencion` según el libro de códigos, y controla que el filtro de P1 se haya
respetado (quien respondió "Nunca" no debe tener datos en P2–P4).
