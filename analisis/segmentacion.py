"""
Tarea 5.2: elección de k, proyección PCA en 2D y perfil de cada grupo.

Usa las MISMAS funciones que exponen las tools del servidor:
  - kmeans_utils.cargar_y_escalar / ejecutar_kmeans  (tool segmentar_kmeans)
  - pca_utils.ejecutar_pca                            (tool ejecutar_pca, Tarea 5.1)
La proyección 2D se calcula con las cargas que devuelve ejecutar_pca, no con un PCA
aparte: coordenadas = datos escalados x cargas.

Criterio para elegir k (codo confirmado con silueta, como en clase con Iris):
  1. Codo: el k más grande en el que agregar ese grupo todavía reduce la inercia en al
     menos 10 %. Después de ese punto, cada grupo adicional aporta poco.
  2. Confirmación con silueta: ese k debe ser un máximo local de la silueta (mayor que
     la de k-1 y la de k+1). Si no lo es, el script lo avisa.
  3. Reproducibilidad: la partición debe salir igual con 10 semillas distintas (ARI).

Uso:  python3 analisis/segmentacion.py
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
import kmeans_utils  # noqa: E402
import pca_utils  # noqa: E402

DATASET = "casos_migratorios"
K_RANGO = range(2, 11)
SEMILLAS = range(10)
UMBRAL_CODO = 10.0  # % mínimo de reducción de inercia al agregar un grupo
FIG = RAIZ / "analisis" / "figuras"
RES = RAIZ / "analisis" / "resultados"

# Paleta categórica validada (5 tonos) + formas distintas como segunda codificación.
COLORES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4"]
MARCAS = ["o", "s", "^", "D", "v"]
TINTA, TINTA2, REJILLA, FONDO = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"


def estilo(ax):
    ax.set_facecolor(FONDO)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(REJILLA)
    ax.tick_params(colors=TINTA2, labelsize=9)
    ax.grid(color=REJILLA, linewidth=0.6)
    ax.set_axisbelow(True)


def tabla_k(X):
    filas, previa = [], KMeans(1, n_init=kmeans_utils.N_INIT, random_state=42).fit(X).inertia_
    for k in K_RANGO:
        m = KMeans(k, n_init=kmeans_utils.N_INIT, random_state=kmeans_utils.SEMILLA).fit(X)
        etiq = [KMeans(k, n_init=kmeans_utils.N_INIT, random_state=s).fit_predict(X) for s in SEMILLAS]
        ari = np.mean([adjusted_rand_score(etiq[i], etiq[j])
                       for i in range(len(etiq)) for j in range(i + 1, len(etiq))])
        filas.append({
            "k": k,
            "inercia": round(m.inertia_, 1),
            "reduccion_inercia_pct": round((previa - m.inertia_) / previa * 100, 1),
            "silueta": round(silhouette_score(X, m.labels_), 3),
            "estabilidad_ari": round(ari, 3),
            "grupo_mas_pequeno": int(np.bincount(m.labels_).min()),
        })
        previa = m.inertia_
    return pd.DataFrame(filas)


def elegir_k(t):
    candidatos = t[t.reduccion_inercia_pct >= UMBRAL_CODO]
    k = int(candidatos.k.max())
    sil = t.set_index("k").silueta
    if not (sil[k] > sil.get(k - 1, -1) and sil[k] > sil.get(k + 1, -1)):
        print(f"AVISO: k = {k} no es un máximo local de la silueta; revisar el criterio.")
    return k, candidatos.k.tolist()


def grafico_k(t, k):
    fig, ejes = plt.subplots(1, 3, figsize=(12, 3.6), facecolor=FONDO)
    paneles = [("inercia", "Inercia (codo)", None),
               ("silueta", "Coeficiente de silueta", None),
               ("estabilidad_ari", "Reproducibilidad entre 10 semillas (ARI)", (0.8, 1.01))]
    for ax, (col, titulo, lim) in zip(ejes, paneles):
        estilo(ax)
        ax.plot(t.k, t[col], color=COLORES[0], linewidth=2, marker="o", markersize=6,
                markeredgecolor=FONDO, markeredgewidth=1.5)
        fila = t[t.k == k].iloc[0]
        ax.plot([k], [fila[col]], marker="o", markersize=11, color=COLORES[1],
                markeredgecolor=FONDO, markeredgewidth=2, zorder=5)
        texto = (f"k = {k}\n{fila[col]:,.3f}" if col != "inercia"
                 else f"k = {k}: último grupo que\nreduce la inercia ≥ {UMBRAL_CODO:.0f} %\n"
                      f"({fila.reduccion_inercia_pct} %; k = {k + 1}: "
                      f"{t[t.k == k + 1].iloc[0].reduccion_inercia_pct} %)")
        desplaz = (10, -34) if col == "estabilidad_ari" else (10, 8)
        ax.annotate(texto, (k, fila[col]), textcoords="offset points", xytext=desplaz,
                    fontsize=9, color=TINTA)
        ax.set_title(titulo, fontsize=10.5, color=TINTA, loc="left")
        ax.set_xlabel("k (número de grupos)", fontsize=9, color=TINTA2)
        ax.set_xticks(list(K_RANGO))
        if lim:
            ax.set_ylim(*lim)
    fig.tight_layout()
    fig.savefig(FIG / "eleccion_k.png", dpi=200, facecolor=FONDO)
    plt.close(fig)


def proyeccion_pca(X, numericas):
    pca = pca_utils.ejecutar_pca(DATASET, 2)  # la misma función que la tool ejecutar_pca
    cargas = np.array([[pca["cargas"][pc][v] for pc in ("PC1", "PC2")] for v in numericas])
    return X @ cargas, pca


def grafico_pca(Z, etiquetas, nombres, pca):
    v1, v2 = pca["varianza_explicada_por_componente"]
    fig, ax = plt.subplots(figsize=(8.2, 6), facecolor=FONDO)
    estilo(ax)
    rng = np.random.default_rng(42)
    Zj = Z + rng.normal(0, 0.04, Z.shape)  # leve dispersión: muchas variables son 0/1
    for g in range(len(nombres)):
        m = etiquetas == g
        ax.scatter(Zj[m, 0], Zj[m, 1], s=18, alpha=0.55, color=COLORES[g], marker=MARCAS[g],
                   edgecolors=FONDO, linewidths=0.4,
                   label=f"{nombres[g]} (n = {m.sum():,})")
    ax.set_xlabel(f"Componente 1 ({v1:.1%} de la varianza)", fontsize=10, color=TINTA2)
    ax.set_ylabel(f"Componente 2 ({v2:.1%} de la varianza)", fontsize=10, color=TINTA2)
    ax.set_title(f"Grupos de K-Means proyectados con PCA: el plano conserva "
                 f"{pca['varianza_acumulada']:.1%} de la varianza",
                 fontsize=11, color=TINTA, loc="left")
    leg = ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, frameon=False,
                    fontsize=9, markerscale=1.6)
    for txt in leg.get_texts():
        txt.set_color(TINTA)
    fig.tight_layout()
    fig.savefig(FIG / "pca_2d_grupos.png", dpi=200, facecolor=FONDO)
    plt.close(fig)


def perfil(filas_usadas, etiquetas):
    fuente = pd.read_csv(RAIZ / "analisis" / "fuente" / "casos_migratorios_tarea42.csv")
    datos = pd.read_csv(pca_utils._ruta_dataset(DATASET))
    numericas = datos.select_dtypes(include="number").columns
    mascara = datos[numericas].notna().all(axis=1).to_numpy()
    resultado = fuente[mascara].reset_index(drop=True)
    assert (resultado.id_expediente == filas_usadas.id_expediente).all()
    resultado["grupo"] = etiquetas
    agil = resultado.tipo_caso.isin(["miedo_creible", "reinstalacion"])
    p = resultado.assign(agil=agil).groupby("grupo").agg(
        casos=("grupo", "size"),
        edad_media=("edad", "mean"),
        dependientes_media=("num_dependientes", "mean"),
        pct_detenido=("detenido", lambda s: (s == "si").mean() * 100),
        pct_con_fianza=("solicito_fianza", lambda s: (s == "si").mean() * 100),
        pct_antecedentes=("antecedentes_penales", lambda s: (s == "si").mean() * 100),
        pct_abogado=("representacion_legal", lambda s: (s == "si").mean() * 100),
        pct_interprete=("requiere_interprete", lambda s: (s == "si").mean() * 100),
        pct_asilo=("tipo_caso", lambda s: (s == "asilo").mean() * 100),
        pct_proceso_agil=("agil", lambda s: s.mean() * 100),
        dias_mediana=("dias_hasta_resolucion", "median"),
        aplazamientos_media=("aplazamientos", "mean"),
    ).round(1)
    return p


def nombrar(p):
    nombres = {}
    for g, r in p.iterrows():
        if r.pct_antecedentes > 50:
            nombres[g] = "Con antecedentes penales"
        elif r.dependientes_media > 1.5:
            nombres[g] = "Familias con dependientes"
        elif r.pct_detenido < 50:
            nombres[g] = "No detenidos"
        elif r.pct_con_fianza > 50:
            nombres[g] = "Detenidos que pidieron fianza"
        else:
            nombres[g] = "Detenidos sin fianza (vía rápida)"
    return [nombres[g] for g in sorted(nombres)]


def main():
    filas, X, numericas = kmeans_utils.cargar_y_escalar(DATASET)
    t = tabla_k(X)
    k, candidatos = elegir_k(t)
    t.to_csv(RES / "tabla_eleccion_k.csv", index=False)
    grafico_k(t, k)

    seg = kmeans_utils.ejecutar_kmeans(DATASET, k)  # la misma función que la tool
    etiquetas = np.array(seg["etiquetas"])
    p = perfil(filas, etiquetas)
    nombres = nombrar(p)
    p.insert(0, "nombre", nombres)
    p.to_csv(RES / "perfil_grupos.csv")

    Z, pca = proyeccion_pca(X, numericas)
    grafico_pca(Z, etiquetas, nombres, pca)

    resumen = {"dataset": DATASET, "filas_usadas": seg["filas_usadas"], "k_elegido": k,
               "candidatos_codo": candidatos, "silueta": seg["silueta"],
               "pca_varianza_por_componente": pca["varianza_explicada_por_componente"],
               "pca_varianza_acumulada_2d": pca["varianza_acumulada"],
               "tamano_por_grupo": seg["tamano_por_grupo"]}
    (RES / "resumen.json").write_text(json.dumps(resumen, ensure_ascii=False, indent=2))
    print(t.to_string(index=False))
    print(f"\nCandidatos por el codo (>= {UMBRAL_CODO} %): {candidatos} -> k elegido = {k}")
    print(p.to_string())
    print(json.dumps(resumen, ensure_ascii=False))


if __name__ == "__main__":
    main()
