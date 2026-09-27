"""
Reglas difusas del sistema de compatibilidad.
Operadores de skfuzzy: & = AND (min), | = OR (max), ~ = NOT (1 - mu).
"""
from skfuzzy import control as ctrl


def crear_reglas(edad, afin, dist, comp):
    """Devuelve la lista de las 11 reglas difusas."""
    return [
        # FR1 afinidad alta Y distancia cerca -> alta
        ctrl.Rule(afin["alta"] & dist["cerca"], comp["alta"]),
        # FR2 muy(afinidad alta) Y NO(edad grande) -> alta
        ctrl.Rule(afin["muy_alta"] & ~edad["grande"], comp["alta"]),
        # FR3 afinidad media Y edad pequena -> media
        ctrl.Rule(afin["media"] & edad["pequena"], comp["media"]),
        # FR4 afinidad baja -> baja
        ctrl.Rule(afin["baja"], comp["baja"]),
        # FR5 distancia lejos Y NO(afinidad alta) -> baja
        ctrl.Rule(dist["lejos"] & ~afin["alta"], comp["baja"]),
        # FR6 edad grande O distancia lejos -> baja
        ctrl.Rule(edad["grande"] | dist["lejos"], comp["baja"]),
        # FR7 afinidad alta Y edad moderada -> media
        ctrl.Rule(afin["alta"] & edad["moderada"], comp["media"]),
        # FR8 afinidad media Y mas o menos(distancia lejos) -> media
        ctrl.Rule(afin["media"] & dist["mas_o_menos_lejos"], comp["media"]),
        # FR9 afinidad alta Y distancia lejos -> media
        ctrl.Rule(afin["alta"] & dist["lejos"], comp["media"]),
        # FR10 NO(afinidad baja) Y distancia intermedia -> media
        ctrl.Rule(~afin["baja"] & dist["intermedia"], comp["media"]),
        # FR11 afinidad media Y distancia cerca -> media
        ctrl.Rule(afin["media"] & dist["cerca"], comp["media"]),
    ]
