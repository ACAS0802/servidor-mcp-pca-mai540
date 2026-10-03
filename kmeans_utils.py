"""
Lógica de segmentación con K-Means: nada de esto sabe que existe MCP.

Mismo patrón que pca_utils.py (Tarea 5.2): primero la lógica aquí, y solo después
el decorador en mcp_server.py. Reutiliza pca_utils._ruta_dataset, así que hereda la
lista de permitidos de la Tarea 5.1: solo se leen archivos .csv de datasets/.

Mismas filas que el PCA: se usan las columnas numéricas y se descartan las filas con
algún faltante (igual que pca_utils.ejecutar_pca), para que la proyección en 2D y las
etiquetas de K-Means correspondan fila por fila.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

import pca_utils

SEMILLA = 42
N_INIT = 10


def cargar_y_escalar(nombre: str) -> tuple[pd.DataFrame, np.ndarray, list[str]]:
    """Carga un dataset de datasets/ y estandariza sus columnas numéricas.

    Devuelve las filas usadas (sin faltantes en las numéricas), la matriz escalada
    y los nombres de las columnas numéricas.
    """
    df = pd.read_csv(pca_utils._ruta_dataset(nombre))
    numericas = df.select_dtypes(include="number").columns.tolist()
    if not numericas:
        raise ValueError(f"'{nombre}' no tiene columnas numéricas para segmentar.")
    filas = df.dropna(subset=numericas).reset_index(drop=True)
    X = StandardScaler().fit_transform(filas[numericas])
    return filas, X, numericas


def ejecutar_kmeans(nombre: str, k: int) -> dict:
    """Corre K-Means con k grupos sobre las columnas numéricas escaladas.

    Devuelve las etiquetas de cada fila, la inercia, el coeficiente de silueta, el
    tamaño de cada grupo y el promedio de cada variable por grupo (en sus unidades
    originales), que es lo que permite describir qué caracteriza a cada grupo.
    """
    filas, X, numericas = cargar_y_escalar(nombre)
    if k < 2 or k > min(10, len(filas) - 1):
        raise ValueError(
            f"k debe estar entre 2 y {min(10, len(filas) - 1)}: la silueta necesita "
            "al menos 2 grupos."
        )

    modelo = KMeans(n_clusters=k, n_init=N_INIT, random_state=SEMILLA).fit(X)
    etiquetas = modelo.labels_
    tamanos = np.bincount(etiquetas, minlength=k)
    perfil = filas[numericas].groupby(etiquetas).mean()

    return {
        "dataset": nombre,
        "k": k,
        "filas_usadas": len(filas),
        "variables": numericas,
        "etiquetas": [int(e) for e in etiquetas],
        "tamano_por_grupo": {f"grupo_{g}": int(n) for g, n in enumerate(tamanos)},
        "inercia": round(float(modelo.inertia_), 2),
        "silueta": round(float(silhouette_score(X, etiquetas)), 4),
        "promedios_por_grupo": {
            f"grupo_{g}": {col: round(float(v), 3) for col, v in perfil.loc[g].items()}
            for g in perfil.index
        },
    }
