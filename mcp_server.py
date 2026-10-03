"""
Servidor MCP: tres tools, dos resources, un prompt (la tercera tool, segmentar_kmeans, es de la Tarea 5.2).

Este es el archivo que el profesor completa en vivo durante la Clase 5.1,
siguiendo el mismo patrón del curso de Anthropic "Introduction to Model
Context Protocol" (M02), adaptado de un chatbot de documentos a un
servidor de análisis de datos.

Tools    -> operaciones que Claude puede decidir ejecutar (cargar un dataset,
            correr PCA).
Resources -> datos que el cliente puede pedir directamente, sin pasar por
            una decisión de Claude (la lista de datasets, la ficha de uno).
Prompt   -> una plantilla ya evaluada para una tarea recurrente: interpretar
            componentes principales en términos del dominio, no solo en
            términos de varianza.

ESTADO: COMPLETO (Tarea 5.1, Araceli Castillo).
Los cinco bloques "# TODO" se dejaron como referencia; debajo de cada uno está
la pieza implementada (un commit por pieza). Dos cambios surgieron de la
verificación en el Inspector: _como_error_de_tool (los errores llegan al cliente
con su motivo) y la lista de permitidos en pca_utils._ruta_dataset (un nombre
con ../ ya no sale de datasets/). Ver PERMISOS.md y evidencia/.

Para probar este archivo una vez completado, sin cliente ni CLI:
    mcp dev mcp_server.py
Abre el Inspector en el navegador, conecta, y prueba cada tool/resource/prompt
a mano antes de conectarlo a nada más.
"""

from mcp.server.mcpserver import MCPServer, UserMessage
from mcp.server.mcpserver.exceptions import ToolError
from pydantic import Field

import kmeans_utils
import pca_utils

mcp = MCPServer("analisis-datos")


def _como_error_de_tool(funcion, *args):
    """Convierte los ValueError de pca_utils en ToolError.

    Sin esto, el SDK trata un ValueError como un fallo inesperado y el cliente
    solo ve "Error executing tool ...", sin el motivo. Con ToolError, Claude
    recibe el mensaje (por ejemplo, la lista de datasets disponibles o el rango
    válido de n_componentes) y puede corregir su siguiente llamada.
    """
    try:
        return funcion(*args)
    except ValueError as e:
        raise ToolError(str(e)) from e


# ---------------------------------------------------------------------------
# Tools — algo que Claude DECIDE ejecutar, con los argumentos que el modelo
# elige según lo que pida quien está conversando.
# ---------------------------------------------------------------------------

# TODO 1 — tool "cargar_dataset"
#   Decorador:   @mcp.tool(name="cargar_dataset", description="...")
#   Función:     cargar_dataset(nombre: str = Field(...)) -> dict
#   Cuerpo:      return pca_utils.describir_dataset(nombre)
#   La descripción debe explicar que esta tool se usa ANTES de ejecutar_pca,
#   para que Claude sepa qué columnas numéricas tiene el dataset.

@mcp.tool(
    name="cargar_dataset",
    description=(
        "Carga uno de los datasets disponibles y describe su forma: número de "
        "filas, columnas numéricas y columnas categóricas. Úsala ANTES de "
        "ejecutar_pca, para saber qué columnas numéricas tiene el dataset y "
        "cuántos componentes se pueden pedir como máximo (uno por columna "
        "numérica). Solo acepta nombres de la lista data://datasets."
    ),
)
def cargar_dataset(
    nombre: str = Field(description="Nombre del dataset, sin la extensión .csv (por ejemplo: 'iris')."),
) -> dict:
    return _como_error_de_tool(pca_utils.describir_dataset, nombre)


# TODO 2 — tool "ejecutar_pca"
#   Decorador:   @mcp.tool(name="ejecutar_pca", description="...")
#   Función:     ejecutar_pca(nombre: str = Field(...),
#                              n_componentes: int = Field(...)) -> dict
#   Cuerpo:      return pca_utils.ejecutar_pca(nombre, n_componentes)
#   La descripción debe mencionar que devuelve varianza explicada, varianza
#   acumulada y las cargas (loadings) de cada variable original.

@mcp.tool(
    name="ejecutar_pca",
    description=(
        "Ejecuta PCA (análisis de componentes principales) sobre las columnas "
        "numéricas de un dataset, después de estandarizarlas. Devuelve la "
        "varianza explicada por cada componente, la varianza acumulada y las "
        "cargas (loadings) de cada variable original en cada componente, que "
        "son lo que permite interpretar qué representa cada componente. Usa "
        "cargar_dataset antes para saber cuántas columnas numéricas hay: "
        "n_componentes debe estar entre 1 y ese número."
    ),
)
def ejecutar_pca(
    nombre: str = Field(description="Nombre del dataset, sin la extensión .csv (por ejemplo: 'iris')."),
    n_componentes: int = Field(description="Número de componentes principales a calcular (mínimo 1)."),
) -> dict:
    return _como_error_de_tool(pca_utils.ejecutar_pca, nombre, n_componentes)


# Tarea 5.2 — tool "segmentar_kmeans"
#   Mismo patrón que ejecutar_pca: la lógica vive en kmeans_utils.py y aquí
#   solo se envuelve con el decorador.

@mcp.tool(
    name="segmentar_kmeans",
    description=(
        "Segmenta un dataset con K-Means sobre sus columnas numéricas "
        "estandarizadas. Devuelve la etiqueta de grupo de cada fila, el tamaño "
        "de cada grupo, la inercia, el coeficiente de silueta del k elegido y el "
        "promedio de cada variable por grupo (en sus unidades originales), que "
        "sirve para describir qué caracteriza a cada grupo. k debe estar entre 2 "
        "y 10. Usa las mismas filas que ejecutar_pca, así que las etiquetas se "
        "pueden combinar con su proyección."
    ),
)
def segmentar_kmeans(
    nombre: str = Field(description="Nombre del dataset, sin la extensión .csv (por ejemplo: 'casos_migratorios')."),
    k: int = Field(description="Número de grupos (entre 2 y 10)."),
) -> dict:
    return _como_error_de_tool(kmeans_utils.ejecutar_kmeans, nombre, k)


# ---------------------------------------------------------------------------
# Resources — datos que el CLIENTE pide directamente, sin que Claude decida
# nada. Estático (siempre lo mismo) o con plantilla (un parámetro en la URI).
# ---------------------------------------------------------------------------

# TODO 3 — resource estático "data://datasets"
#   Decorador:   @mcp.resource("data://datasets", mime_type="application/json")
#   Función:     listar_datasets() -> list[str]
#   Cuerpo:      return pca_utils.listar_datasets()

@mcp.resource(
    "data://datasets",
    mime_type="application/json",
    description="Lista de los datasets disponibles en la carpeta datasets/ (nombres sin .csv).",
)
def listar_datasets() -> list[str]:
    return pca_utils.listar_datasets()


# TODO 4 — resource con plantilla "data://datasets/{nombre}"
#   Decorador:   @mcp.resource("data://datasets/{nombre}", mime_type="application/json")
#   Función:     ficha_dataset(nombre: str) -> dict
#   Cuerpo:      return pca_utils.describir_dataset(nombre)
#   El framework extrae automáticamente lo que haya entre {llaves} en la URI
#   que pida el cliente y lo pasa como argumento "nombre".

@mcp.resource(
    "data://datasets/{nombre}",
    mime_type="application/json",
    description="Ficha de un dataset: filas, columnas numéricas y columnas categóricas.",
)
def ficha_dataset(nombre: str) -> dict:
    return pca_utils.describir_dataset(nombre)


# ---------------------------------------------------------------------------
# Prompt — una plantilla YA EVALUADA para una tarea que se repite, en vez de
# dejar que cada usuario improvise su propia pregunta de interpretación.
# ---------------------------------------------------------------------------

# TODO 5 — prompt "interpretar_componentes"
#   Decorador:   @mcp.prompt(name="interpretar_componentes", description="...")
#   Función:     interpretar_componentes(nombre: str = Field(...),
#                                         n_componentes: int = Field(...)
#                                         ) -> list[UserMessage]
#   Cuerpo:      construir un f-string "prompt" que le pida a Claude, sobre el
#                resultado de ejecutar_pca:
#                  1. identificar las 2-3 variables con mayor carga por componente
#                  2. explicar qué patrón de dominio podría representar cada una
#                  3. indicar si el signo de la carga tiene una lectura razonable
#                y terminar preguntando si n_componentes alcanza según la
#                varianza acumulada.
#   Devolver:    return [UserMessage(prompt)]
#   Ver el texto exacto sugerido en la diapositiva 12.

@mcp.prompt(
    name="interpretar_componentes",
    description=(
        "Interpreta los componentes principales de un dataset en términos del "
        "dominio, no solo de la varianza: variables dominantes, patrón que "
        "representan, lectura del signo y si el número de componentes alcanza."
    ),
)
def interpretar_componentes(
    nombre: str = Field(description="Nombre del dataset a interpretar (por ejemplo: 'iris')."),
    n_componentes: int = Field(description="Número de componentes principales a interpretar."),
) -> list[UserMessage]:
    prompt = f"""Usa la tool ejecutar_pca sobre el dataset "{nombre}" con {n_componentes} componentes.
Con base en el resultado, para cada componente principal:

1. Identifica las 2-3 variables con mayor carga en valor absoluto.
2. Explica qué patrón del dominio de "{nombre}" podría representar ese componente,
   en el lenguaje de quien conoce esos datos, no solo en términos de varianza.
3. Indica si el signo de las cargas tiene una lectura razonable (qué variables
   suben juntas y cuáles se mueven en sentido contrario).

Termina respondiendo esta pregunta: según la varianza acumulada, ¿alcanzan
{n_componentes} componentes para describir "{nombre}", o haría falta otro?
No inventes variables ni valores que no estén en el resultado de la tool."""
    return [UserMessage(prompt)]


if __name__ == "__main__":
    mcp.run(transport="stdio")
