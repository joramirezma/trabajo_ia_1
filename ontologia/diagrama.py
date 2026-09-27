"""
Dibuja el diagrama de clases de la ontologia leyendo el .ttl.
Flechas solidas: rdfs:subClassOf. Flechas punteadas: propiedades entre clases (dominio -> rango).
"""
import os

import matplotlib
import matplotlib.pyplot as plt
from rdflib import Graph, RDF, RDFS

# posicion de cada clase en el dibujo (solo para que se vea ordenado)
POSICIONES = {
    "Person": (1.0, 9.0), "Persona": (1.0, 7.0),
    "Estudiante": (0.0, 5.0), "Profesional": (2.0, 5.0),
    "Interes": (6.0, 9.0), "Deporte": (6.0, 6.0),
    "Valor": (9.5, 9.0), "ObjetivoRelacion": (9.5, 4.5),
    "Lugar": (6.0, 3.0), "Ciudad": (4.5, 1.0), "LugarDeCita": (7.5, 1.0),
    "Cita": (1.0, 2.5),
}


def corto(uri):
    """Nombre local de un URI."""
    return str(uri).split("#")[-1].split("/")[-1]


def dibujar_diagrama(ruta_ttl, carpeta="docs"):
    """Genera docs/diagrama_clases.png a partir de la ontologia."""
    g = Graph()
    g.parse(ruta_ttl, format="turtle")
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.axis("off")

    for nombre, (x, y) in POSICIONES.items():
        ax.text(x, y, nombre, ha="center", va="center", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.4", fc="#dbe9f6", ec="#2b5d8a"))

    def flecha(o, d, estilo, color, texto=""):
        """Dibuja una flecha de la clase o a la clase d (o un bucle si son iguales)."""
        (x1, y1), (x2, y2) = POSICIONES[o], POSICIONES[d]
        if o == d:
            ax.annotate("", xy=(x1 - 0.2, y1 + 0.2), xytext=(x1 + 0.2, y1 + 0.2),
                        arrowprops=dict(arrowstyle="->", color=color, ls=estilo,
                                        connectionstyle="arc3,rad=1.8"))
            ax.text(x1, y1 + 0.75, texto, fontsize=8, color=color, ha="center")
            return
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color=color, ls=estilo,
                                    shrinkA=18, shrinkB=18))
        if texto:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2, texto, fontsize=8, color=color,
                    ha="center", bbox=dict(fc="white", ec="none", pad=0.5))

    for s, o in g.subject_objects(RDFS.subClassOf):
        if corto(s) in POSICIONES and corto(o) in POSICIONES:
            flecha(corto(s), corto(o), "-", "black", "subClassOf")

    for p in g.subjects(RDF.type, RDF.Property):
        dom, ran = g.value(p, RDFS.domain), g.value(p, RDFS.range)
        if dom is None or ran is None:
            continue
        if corto(dom) in POSICIONES and corto(ran) in POSICIONES:
            flecha(corto(dom), corto(ran), "--", "#b0501c", corto(p))

    # propiedades con rango literal, listadas bajo su clase
    literales = {}
    for p in g.subjects(RDF.type, RDF.Property):
        dom, ran = g.value(p, RDFS.domain), g.value(p, RDFS.range)
        if ran is not None and "XMLSchema" in str(ran):
            literales.setdefault(corto(dom), []).append(f"{corto(p)}: xsd:{corto(ran)}")
    for clase, props in literales.items():
        x, y = POSICIONES[clase]
        ax.text(x, y - 0.45, "\n".join(props), ha="center", va="top", fontsize=7.5, color="#444")

    ax.set_xlim(-1, 11)
    ax.set_ylim(0, 10)
    ax.set_title("Ontología de emparejamiento (mt:)")
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "diagrama_clases.png")
    fig.savefig(ruta, dpi=120, bbox_inches="tight")
    plt.close(fig)
    return ruta


if __name__ == "__main__":
    matplotlib.use("Agg")
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    print(dibujar_diagrama(os.path.join(base, "ontologia", "emparejamiento.ttl"),
                           os.path.join(base, "docs")))
