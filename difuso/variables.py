"""
Variables difusas, universos y funciones de pertenencia.
"""
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


def muy(mf):
    """Modificador 'muy' (concentracion): mu(x)^2."""
    return np.power(mf, 2)


def mas_o_menos(mf):
    """Modificador 'mas o menos' (dilatacion): mu(x)^0.5."""
    return np.power(mf, 0.5)


def crear_variables():
    """Crea las 3 entradas y la salida con sus valores linguisticos.

    Devuelve (diferencia_edad, afinidad_intereses, distancia_km, compatibilidad).
    """
    # Universos del discurso
    diferencia_edad = ctrl.Antecedent(np.arange(0, 30.1, 0.1), "diferencia_edad")       # años
    afinidad_intereses = ctrl.Antecedent(np.arange(0, 100.1, 0.5), "afinidad_intereses")  # %
    distancia_km = ctrl.Antecedent(np.arange(0, 150.1, 0.5), "distancia_km")              # km
    compatibilidad = ctrl.Consequent(np.arange(0, 100.1, 0.5), "compatibilidad")

    u = diferencia_edad.universe
    diferencia_edad["pequena"] = fuzz.trapmf(u, [0, 0, 3, 7])
    diferencia_edad["moderada"] = fuzz.trimf(u, [4, 9, 14])
    diferencia_edad["grande"] = fuzz.trapmf(u, [11, 18, 30, 30])

    u = afinidad_intereses.universe
    afinidad_intereses["baja"] = fuzz.trapmf(u, [0, 0, 15, 35])
    afinidad_intereses["media"] = fuzz.gaussmf(u, 45, 12)
    afinidad_intereses["alta"] = fuzz.trapmf(u, [50, 70, 100, 100])
    # modificador aplicado como un termino nuevo
    afinidad_intereses["muy_alta"] = muy(afinidad_intereses["alta"].mf)

    u = distancia_km.universe
    distancia_km["cerca"] = fuzz.gaussmf(u, 0, 10)
    distancia_km["intermedia"] = fuzz.trimf(u, [10, 40, 80])
    distancia_km["lejos"] = fuzz.trapmf(u, [60, 100, 150, 150])
    distancia_km["mas_o_menos_lejos"] = mas_o_menos(distancia_km["lejos"].mf)

    u = compatibilidad.universe
    compatibilidad["baja"] = fuzz.trimf(u, [0, 0, 45])
    compatibilidad["media"] = fuzz.gaussmf(u, 50, 12)
    compatibilidad["alta"] = fuzz.trimf(u, [55, 100, 100])
    compatibilidad.defuzzify_method = "centroid"

    return diferencia_edad, afinidad_intereses, distancia_km, compatibilidad
