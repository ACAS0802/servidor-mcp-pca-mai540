"""
Servidor MCP: dos tools, dos resources, un prompt.

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

ESTADO: INCOMPLETO A PROPÓSITO.
Cada bloque "# TODO" de abajo es una pieza que se escribe en vivo durante la
clase, siguiendo el patrón de @mcp.tool / @mcp.resource / @mcp.prompt que ya
viste en las diapositivas 10, 11 y 12. La lógica de negocio (pca_utils.py) ya
está completa — aquí solo falta envolverla con el decorador correcto.

Para probar este archivo una vez completado, sin cliente ni CLI:
    mcp dev mcp_server.py
Abre el Inspector en el navegador, conecta, y prueba cada tool/resource/prompt
a mano antes de conectarlo a nada más.
"""

from mcp.server.mcpserver import MCPServer, UserMessage
from pydantic import Field

import pca_utils

mcp = MCPServer("analisis-datos")


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


# TODO 2 — tool "ejecutar_pca"
#   Decorador:   @mcp.tool(name="ejecutar_pca", description="...")
#   Función:     ejecutar_pca(nombre: str = Field(...),
#                              n_componentes: int = Field(...)) -> dict
#   Cuerpo:      return pca_utils.ejecutar_pca(nombre, n_componentes)
#   La descripción debe mencionar que devuelve varianza explicada, varianza
#   acumulada y las cargas (loadings) de cada variable original.


# ---------------------------------------------------------------------------
# Resources — datos que el CLIENTE pide directamente, sin que Claude decida
# nada. Estático (siempre lo mismo) o con plantilla (un parámetro en la URI).
# ---------------------------------------------------------------------------

# TODO 3 — resource estático "data://datasets"
#   Decorador:   @mcp.resource("data://datasets", mime_type="application/json")
#   Función:     listar_datasets() -> list[str]
#   Cuerpo:      return pca_utils.listar_datasets()


# TODO 4 — resource con plantilla "data://datasets/{nombre}"
#   Decorador:   @mcp.resource("data://datasets/{nombre}", mime_type="application/json")
#   Función:     ficha_dataset(nombre: str) -> dict
#   Cuerpo:      return pca_utils.describir_dataset(nombre)
#   El framework extrae automáticamente lo que haya entre {llaves} en la URI
#   que pida el cliente y lo pasa como argumento "nombre".


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


if __name__ == "__main__":
    mcp.run(transport="stdio")
