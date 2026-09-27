"""
Carga de la ontologia y razonamiento RDFS con OWL-RL.
"""
from rdflib import Graph, RDF, RDFS, Namespace
from owlrl import DeductiveClosure, RDFS_Semantics

MT = Namespace("http://ejemplo.org/emparejamiento#")


def cargar_y_razonar(ruta_ttl):
    """Devuelve (grafo_original, grafo_inferido) tras DeductiveClosure(RDFS_Semantics).

    Se parsea el archivo dos veces porque el razonador modifica el grafo
    sobre el que trabaja, y el original se necesita para saber que es inferido.
    """
    g_original = Graph()
    g_original.parse(ruta_ttl, format="turtle")

    g_inferido = Graph()
    g_inferido.parse(ruta_ttl, format="turtle")
    DeductiveClosure(RDFS_Semantics).expand(g_inferido)
    return g_original, g_inferido


def nuevos_hechos(g_original, g_inferido):
    """Triples que estan en el grafo inferido y no en el original,
    dejando solo los que tienen sujeto del namespace mt."""
    return [t for t in g_inferido
            if t not in g_original and str(t[0]).startswith(str(MT))]


def casos_inferencia(g_original, g_inferido):
    """Arma los ejemplos de los tres casos pedidos a partir de lo inferido.

    caso 1: tipo por jerarquia de clases (subClassOf)
    caso 2: tipo por dominio/rango de una propiedad (individuo sin rdf:type)
    caso 3: nuevo hecho por subPropertyOf
    """
    nuevos = set(nuevos_hechos(g_original, g_inferido))

    caso1 = []
    for s, _, c in g_original.triples((None, RDF.type, None)):
        for sup in g_original.objects(c, RDFS.subClassOf):
            if (s, RDF.type, sup) in nuevos:
                caso1.append((s, RDF.type, sup))

    caso2 = []
    for s in set(g_original.subjects()):
        if (s, RDF.type, None) in g_original:
            continue
        for p in set(g_original.predicates(s, None)):
            for c in g_original.objects(p, RDFS.domain):
                if (s, RDF.type, c) in nuevos:
                    caso2.append((s, RDF.type, c, p))

    caso3 = []
    for p, sup in g_original.subject_objects(RDFS.subPropertyOf):
        for s, o in g_original.subject_objects(p):
            if (s, sup, o) in nuevos:
                caso3.append((s, sup, o, p))

    return caso1, caso2, caso3


def mostrar_razonamiento(g_original, g_inferido):
    """Imprime la comparacion antes/despues y los casos de inferencia."""
    g_inferido.bind("mt", MT)
    q = g_inferido.namespace_manager.normalizeUri

    print(f"Triples antes del razonamiento:   {len(g_original)}")
    print(f"Triples despues del razonamiento: {len(g_inferido)}")
    nuevos = nuevos_hechos(g_original, g_inferido)
    print(f"Triples nuevos sobre recursos mt: {len(nuevos)}")

    caso1, caso2, caso3 = casos_inferencia(g_original, g_inferido)

    print("\nCaso 1 - jerarquia de clases (subClassOf):")
    for s, p, o in sorted(caso1)[:8]:
        print(f"   {q(s)} a {q(o)}")
    print(f"   ... total {len(caso1)}")

    print("\nCaso 2 - pertenencia desde el dominio de una propiedad:")
    for s, p, o, prop in caso2:
        print(f"   {q(s)} a {q(o)}   (por el dominio de {q(prop)})")

    print("\nCaso 3 - jerarquia de propiedades (subPropertyOf):")
    for s, p, o, prop in sorted(caso3):
        print(f"   {q(s)} {q(p)} {q(o)}   (desde {q(prop)})")

    print("\nOtros hechos nuevos (muestra):")
    ya_mostrados = set(caso1) | {(s, p, o) for s, p, o, _ in caso2 + caso3}
    otros = [t for t in nuevos if t[1] == RDF.type and t[2] != RDFS.Resource
             and t not in ya_mostrados]
    for s, p, o in sorted(otros)[:8]:
        print(f"   {q(s)} a {q(o)}")
