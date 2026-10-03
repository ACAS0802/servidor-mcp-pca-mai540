# Evidencia de verificación — Tarea 5.1

Cada imagen muestra a la izquierda la **petición** en el MCP Inspector (v2.9.0) y a la
derecha la **respuesta del servidor**. Servidor lanzado con `mcp dev mcp_server.py`
(mcp 2.3.0, Python 3.11).

## Las 5 piezas

| # | Pieza | Petición | Resultado esperado | Imagen |
|---|---|---|---|---|
| 1 | Tool `cargar_dataset` | `nombre="iris"` | 150 filas, 4 numéricas, 1 categórica (`species`) | `1_tool_cargar_dataset.png` |
| 2 | Tool `ejecutar_pca` | `nombre="iris"`, `n_componentes=2` | Varianza 0.7296 + 0.2285 = **0.9581**; cargas de PC1 y PC2 | `2_tool_ejecutar_pca.png` |
| 3 | Resource `data://datasets` | — | `["iris", "wine"]`, `application/json` | `3_resource_datasets.png` |
| 4 | Resource `data://datasets/{nombre}` | `nombre="wine"` | 178 filas, 13 numéricas, 1 categórica (`cultivar`) | `4_resource_plantilla_wine.png` |
| 5 | Prompt `interpretar_componentes` | `nombre="iris"`, `n_componentes=2` | Un mensaje `user` con los 3 pasos y la pregunta final | `5_prompt_interpretar.png` |

Las cinco respondieron como se esperaba. `0_conexion_inspector.png` muestra la conexión
(initialize, tools/list, resources/list, resources/templates/list, prompts/list: todos OK).

## Lo que la verificación encontró y se corrigió

| Antes | Después | Commit |
|---|---|---|
| `antes_A_lee_csv_fuera_de_datasets.png`: con `nombre="../../mcp/secreto/expedientes"` la tool leía un CSV **fuera** del proyecto (columnas `ssn`, `salario`) | `6_rechazo_fuera_de_datasets.png`: el mismo nombre se rechaza y se listan los permitidos | `Restringe los nombres de dataset…` |
| `antes_B_error_sin_motivo.png`: con `nombre="titanic"` el cliente solo veía *Error executing tool cargar_dataset* | `7_error_n_componentes.png` y `log_verificacion.txt`: el error dice el motivo (datasets disponibles, rango 1–4) | `Hace que los errores de las tools lleguen…` |

El CSV "secreto" era un archivo de prueba de dos filas creado solo para esta comprobación,
fuera del repositorio. No contiene datos reales.

## Log por protocolo

`log_verificacion.txt` repite las mismas pruebas con un cliente MCP propio
(`probar_cliente.py`, stdio), sin navegador: sirve para comprobar el resultado como texto.
Incluye además que el resource con plantilla rechaza una URI con `../` (eso lo hace el SDK).

## Tarea 5.2: tool `segmentar_kmeans`

| Prueba | Petición | Resultado | Imagen |
|---|---|---|---|
| Tool `segmentar_kmeans` | `nombre="casos_migratorios"`, `k=5` | 2,854 filas; grupos de 753, 587, 944, 305 y 265; inercia 12,853.08; **silueta 0.2333**; promedios por grupo; etiquetas al final | `8_tool_segmentar_kmeans.png` |
| k fuera de rango | `k=1` | Se rechaza: *k debe estar entre 2 y 10* | `9_segmentar_kmeans_k_invalido.png` |
| Nombre con `../` | `nombre="../../mcp/secreto/expedientes"` | Se rechaza: hereda la lista de permitidos de la 5.1 | `10_segmentar_kmeans_fuera_de_datasets.png` |

`log_verificacion_5.2.txt` repite estas pruebas por protocolo, más `iris` con `k=3` (silueta
0.4599) y `k=11` (rechazado).
