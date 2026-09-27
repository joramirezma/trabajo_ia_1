"""
Interfaz del modulo difuso que usa la integracion.
"""
import skfuzzy as fuzz
from skfuzzy import control as ctrl

from difuso.variables import crear_variables
from difuso.reglas import crear_reglas

_edad, _afin, _dist, _comp = crear_variables()
_sistema = ctrl.ControlSystem(crear_reglas(_edad, _afin, _dist, _comp))


def nivel_de(score):
    """Valor linguistico de la salida con mayor pertenencia en 'score'."""
    grados = {n: fuzz.interp_membership(_comp.universe, _comp[n].mf, score)
              for n in ("baja", "media", "alta")}
    return max(grados, key=grados.get)


def calcular_compatibilidad(edad_diff, afinidad, distancia_km):
    """Devuelve {'score': float (0-100), 'nivel': 'baja'|'media'|'alta'}.

    Las entradas se recortan al universo de cada variable antes de simular.
    """
    sim = ctrl.ControlSystemSimulation(_sistema)
    sim.input["diferencia_edad"] = min(max(edad_diff, 0), 30)
    sim.input["afinidad_intereses"] = min(max(afinidad, 0), 100)
    sim.input["distancia_km"] = min(max(distancia_km, 0), 150)
    try:
        sim.compute()
        score = float(sim.output["compatibilidad"])
    except (ValueError, KeyError):
        # ninguna regla se activo: se toma como compatibilidad nula
        score = 0.0
    return {"score": round(score, 2), "nivel": nivel_de(score)}
