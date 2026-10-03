"""
Prepara datasets/casos_migratorios.csv a partir de los datos sintéticos de la Tarea 4.2.

Solo pasan a datasets/ (lo único que el servidor MCP puede leer) las variables que se
conocen AL INGRESAR el caso. Las que solo se conocen al cerrarlo (aplazamientos, días
hasta la audiencia final, días hasta la resolución) se quedan en analisis/fuente/: sirven
para describir los grupos después, pero no para formarlos, y el servidor no las expone.

Las variables de sí/no se convierten a 0/1 para que pca_utils y kmeans_utils las traten
como numéricas. id_expediente, tipo_caso, region_origen y tribunal quedan como texto:
no entran al PCA ni al K-Means, pero se usan para describir cada grupo.

Uso:  python3 analisis/preparar_datos.py
"""
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "analisis" / "fuente" / "casos_migratorios_tarea42.csv"
DESTINO = RAIZ / "datasets" / "casos_migratorios.csv"

BINARIAS = ["detenido", "representacion_legal", "requiere_interprete",
            "antecedentes_penales", "solicito_fianza"]
CONTINUAS = ["edad", "meses_en_eeuu", "num_dependientes"]
TEXTO = ["id_expediente", "tipo_caso", "region_origen", "tribunal"]


def main() -> None:
    df = pd.read_csv(FUENTE)
    salida = df[TEXTO + CONTINUAS].copy()
    for col in BINARIAS:
        # "si" -> 1, "no" -> 0; los faltantes se quedan como faltantes (NaN).
        salida[col] = df[col].map({"si": 1, "no": 0})
    salida.to_csv(DESTINO, index=False)
    print(f"{DESTINO.relative_to(RAIZ)}: {len(salida)} filas, "
          f"{len(CONTINUAS) + len(BINARIAS)} columnas numéricas")


if __name__ == "__main__":
    main()
