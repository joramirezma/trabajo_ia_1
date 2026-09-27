"""
Traductor Ontologia -> Sistema experto.

Recorre el grafo ya razonado y convierte cada triple en un Fact generico.
No conoce ningun nombre del dominio: solo usa los IRIs de RDF, RDFS, OWL y XSD,
asi que si se agrega algo al .ttl aparece solo en el motor.
"""
from decimal import Decimal

from rdflib import RDF, RDFS, OWL, XSD, Literal, URIRef

from experto.hechos import Individuo, Relacion, Propiedad, Esquema

# namespaces que se consideran "infraestructura" y no conocimiento del dominio
NS_INFRA = (str(RDF), str(RDFS), str(OWL), str(XSD))

# predicados de RDFS que si describen el esquema del dominio
PRED_ESQUEMA = {
    RDFS.subClassOf: "subClassOf",
    RDFS.subPropertyOf: "subPropertyOf",
    RDFS.domain: "domain",
    RDFS.range: "range",
}

# declaraciones de clase y propiedad (s rdf:type rdfs:Class / rdf:Property)
DECLARACIONES = (RDFS.Class, RDF.Property)


def es_infra(nodo):
    """True si el nodo pertenece a RDF/RDFS/OWL/XSD."""
    return isinstance(nodo, URIRef) and str(nodo).startswith(NS_INFRA)


def traducir(g_inferido, g_original):
    """Traduce el grafo inferido a Facts genericos.

    'origen' = 'inferido' si el triple no esta en g_original, si no 'asertado'.
    """
    facts = []
    # se recorre ordenado para que el orden de los hechos (y la recencia) sea
    # el mismo en todas las ejecuciones
    for s, p, o in sorted(g_inferido):
        # sujetos literales/blank nodes o de infraestructura no aportan al dominio
        if not isinstance(s, URIRef) or es_infra(s):
            continue
        origen = "asertado" if (s, p, o) in g_original else "inferido"

        if p == RDF.type:
            if o in DECLARACIONES:
                facts.append(Esquema(sujeto=str(s), relacion="tipo", objeto=str(o)))
            elif not es_infra(o):
                facts.append(Individuo(uri=str(s), tipo=str(o), origen=origen))
        elif p in PRED_ESQUEMA:
            if isinstance(o, URIRef) and not str(o).startswith(NS_INFRA[:3]):
                facts.append(Esquema(sujeto=str(s), relacion=PRED_ESQUEMA[p], objeto=str(o)))
        elif isinstance(o, Literal):
            if es_infra(p) and p != RDFS.label:
                continue
            tipo = str(o.datatype) if o.datatype else ""
            valor = o.toPython()
            if isinstance(valor, Decimal):
                valor = float(valor)
            facts.append(Propiedad(sujeto=str(s), predicado=str(p),
                                   valor=valor, datatype=tipo))
        elif isinstance(o, URIRef) and not es_infra(p):
            facts.append(Relacion(sujeto=str(s), predicado=str(p),
                                  objeto=str(o), origen=origen))
    return facts


def resumen(facts):
    """Cuenta cuantos Facts hay de cada clase y cuantos son inferidos."""
    conteo = {}
    for f in facts:
        nombre = type(f).__name__
        conteo.setdefault(nombre, [0, 0])
        conteo[nombre][0] += 1
        if f.get("origen") == "inferido":
            conteo[nombre][1] += 1
    return conteo
