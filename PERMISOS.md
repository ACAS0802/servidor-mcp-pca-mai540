# Permisos del servidor `analisis-datos`

## Qué puede hacer

| Pieza | Qué lee | Qué devuelve |
|---|---|---|
| `data://datasets` | Los **nombres** de los `.csv` de `datasets/` | Lista de nombres |
| `cargar_dataset`, `data://datasets/{nombre}` | Un `.csv` de `datasets/` | Número de filas y nombres de columnas |
| `ejecutar_pca` | Las columnas numéricas de un `.csv` de `datasets/` | Varianza explicada, varianza acumulada y cargas |
| `interpretar_componentes` | Nada | Un texto con la plantilla |

Es **solo lectura**: ninguna pieza escribe, borra ni modifica archivos.

## Qué NO expone

- **Archivos fuera de `datasets/`.** Los nombres pasan por una lista de permitidos
  (`pca_utils._ruta_dataset` acepta solo lo que devuelve `listar_datasets()`). Antes del
  cambio, `nombre="../../otra/ruta"` leía cualquier CSV del disco: está documentado en
  `evidencia/antes_A_…png`. El resource con plantilla ya lo rechazaba el SDK.
- **Las filas de los datos.** Ninguna pieza devuelve registros individuales, solo agregados.
  `pca_utils.cargar_dataset`, que sí devuelve el DataFrame completo, **no está decorada**:
  el cliente no la ve.
- **Internet.** Ni `mcp_server.py` ni `pca_utils.py` importan nada de red, y el transporte
  es `stdio`: el servidor no abre ningún puerto.
- **La clave de la API.** `mcp_server.py` no lee `.env`; eso lo hace `main.py`, que es el
  cliente. Al lanzar el servidor sin `env`, el SDK solo le pasa `HOME`, `LC_CTYPE`, `PATH`,
  `SHELL` y `TERM` (comprobado con `ANTHROPIC_API_KEY` definida: no llegó). `.env` está
  en `.gitignore`.
- **Comandos del sistema.** No hay ninguna pieza que ejecute procesos.

## Por qué es el mínimo

Cada permiso responde a una pieza: listar nombres (resource 1), leer un CSV para describirlo
(tool 1 y resource 2) y leer sus columnas numéricas para ajustar el PCA (tool 2). Ninguna de
las cinco necesita escribir, salir de `datasets/`, usar la red ni ver filas individuales, así
que el servidor no lo permite.

## Límites que quedan

- La restricción está **en el código**, no en el sistema operativo: el proceso corre con
  los permisos de mi usuario. Si alguien agrega un `.csv` sensible a `datasets/`, queda
  expuesto (en agregados).
- Con muy pocas filas, los agregados casi revelan los datos: un PCA sobre dos registros
  dice mucho de ellos. Para datos de personas habría que exigir un mínimo de filas.
