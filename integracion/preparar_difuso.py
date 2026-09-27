"""
Prepara las entradas del difuso para cada par de personas y crea los AfinidadDifusa.
"""
from itertools import combinations
from math import radians, sin, cos, asin, sqrt

import vocab as V
from difuso.api import calcular_compatibilidad
from experto.hechos import Individuo, Relacion, Propiedad, AfinidadDifusa


def haversine(lat1, lon1, lat2, lon2):
    """Distancia en km entre dos coordenadas geograficas."""
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    h = sin((lat2 - lat1) / 2) ** 2 + cos(lat1) * cos(lat2) * sin((lon2 - lon1) / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))


def jaccard(i_a, i_b):
    """Afinidad en % como |A n B| / |A u B|. Si ambos estan vacios es 0."""
    union = i_a | i_b
    return 100 * len(i_a & i_b) / len(union) if union else 0.0


def calcular_pares(facts):
    """Para cada par no ordenado de Individuo(tipo=Persona), calcula entradas y llama a difuso."""
    personas = sorted({f["uri"] for f in facts
                       if isinstance(f, Individuo) and f["tipo"] == V.MT_PERSONA})

    intereses, ciudad, edad, coords = {}, {}, {}, {}
    for f in facts:
        if isinstance(f, Relacion):
            if f["predicado"] == V.MT_TIENE_INTERES:
                intereses.setdefault(f["sujeto"], set()).add(f["objeto"])
            elif f["predicado"] == V.MT_VIVE_EN:
                ciudad[f["sujeto"]] = f["objeto"]
        elif isinstance(f, Propiedad):
            if f["predicado"] == V.MT_EDAD:
                edad[f["sujeto"]] = f["valor"]
            elif f["predicado"] == V.MT_LATITUD:
                coords.setdefault(f["sujeto"], [0, 0])[0] = f["valor"]
            elif f["predicado"] == V.MT_LONGITUD:
                coords.setdefault(f["sujeto"], [0, 0])[1] = f["valor"]

    resultado = []
    for a, b in combinations(personas, 2):
        # si falta la edad o la ciudad se toma el peor caso del universo
        edad_diff = abs(edad[a] - edad[b]) if a in edad and b in edad else 30.0
        afin = jaccard(intereses.get(a, set()), intereses.get(b, set()))
        ca, cb = ciudad.get(a), ciudad.get(b)
        if ca in coords and cb in coords:
            dist = haversine(*coords[ca], *coords[cb])
        else:
            dist = 150.0
        r = calcular_compatibilidad(edad_diff, afin, dist)
        resultado.append(AfinidadDifusa(a=a, b=b, edad_diff=float(edad_diff),
                                        afinidad=float(round(afin, 2)), distancia_km=float(round(dist, 2)),
                                        score=float(r["score"]), nivel=r["nivel"]))
    return resultado
