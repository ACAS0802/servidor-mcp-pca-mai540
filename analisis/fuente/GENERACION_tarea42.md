# Cómo se generaron los datos

**Archivo:** `casos_migratorios.csv` · **Generador:** `generar_datos.py` · **Semilla:** 42

El conjunto es **sintético**. La Tarea 4.2 no ofrece un dataset público para Derecho y pide, como opción (b),
generar uno con Claude Code y documentar cómo se generó y qué supuestos asume. Ninguna fila corresponde a una persona,
un expediente, un juez ni un tribunal reales; los tribunales se llaman A a F a propósito. Los valores son **plausibles
para ilustrar el problema**, no estadísticas oficiales.

Correr `python data/generar_datos.py` dos veces produce el mismo archivo byte por byte (MD5 `892fed6f683f71966a583bda3e94176d`).

## Estructura

- 2,000 expedientes → **3,034 filas** (una por persona).
- 1,461 expedientes individuales y 539 familiares (2 a 5 personas).
- 16 columnas: identificador, 12 predictoras, 2 columnas de fuga y el objetivo.

## Supuestos

| # | Supuesto | Cómo está en el generador |
|---|---|---|
| S1 | Los miembros de una familia comparten expediente y se resuelven juntos (solicitante principal y derivados) | Mismo `id_expediente`, mismas características del caso y mismo objetivo; los derivados suman 0–3 días de trámite |
| S2 | La cancelación de remoción exige alrededor de 10 años de presencia | Solo se asigna con `meses_en_eeuu ≥ 120` |
| S3 | El calendario de detenidos se resuelve más rápido | × 0.45 si `detenido = si` |
| S4 | La representación legal alarga el caso (más escritos, pruebas y aplazamientos) | × 1.35 |
| S5 | La duración base depende del tipo de caso | De 30 días (miedo creíble) a 340 (cancelación) |
| S6 | La disponibilidad de intérpretes para idiomas poco comunes es un factor **no observado** que agrega incertidumbre | Ruido lognormal σ = 0.55 para África y Asia con intérprete; σ = 0.30 en el resto |
| S7 | La carga del tribunal tiene un efecto no lineal: por encima de ~3,000 casos por juez los retrasos se aceleran | Factor `(1 + max(0, carga − 3000)/4000)^1.3` y un efecto propio de cada tribunal (0.92 a 1.30) |
| S8 | Los registros del sistema de casos a veces están incompletos | Faltantes al azar: `carga_tribunal` 2 %, `meses_en_eeuu` 4 %, `requiere_interprete` 2 % |

Otros efectos menores: +20 días con intérprete, × 1.15 con antecedentes penales, +18 días con audiencia de fianza,
duración limitada entre 7 y 1,800 días.

## Columnas construidas a propósito para la auditoría

- **Fuga:** `aplazamientos` (Poisson según la duración final) y `dias_hasta_audiencia_final` (el objetivo menos 0–14 días).
  Las dos se calculan **a partir del resultado**, igual que en la realidad solo se conocen al cerrar el caso.
- **Subgrupos:** `region_origen` y `tribunal`, con efectos distintos por construcción (S6 y S7).
- **Entidades repetidas:** los expedientes familiares (S1). Son una característica real del dominio y la decisión de
  incluirlos fue mía al diseñar los datos.

## Limitaciones del propio generador

Las relaciones son las que yo escribí: un modelo que las recupere no demuestra nada sobre tribunales reales. Sirve
para practicar la construcción, la evaluación y la auditoría; no para sacar conclusiones sobre el sistema migratorio.
