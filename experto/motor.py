"""
Motor de inferencia y estrategia de resolucion de conflictos.
"""
from experto.hechos import Recomendacion  # importa primero: aplica el parche de collections
from experta import KnowledgeEngine
from experta.strategies import DepthStrategy

from experto.reglas import ReglasEmparejamiento


class EstrategiaEmparejamiento(DepthStrategy):
    """Ordena la agenda por (salience, specificity, recencia).

    - salience: prioridad declarada en la regla.
    - specificity: cantidad de hechos que empareja la activacion; a igual
      salience gana la regla con mas condiciones (la mas especifica).
    - recencia: ids de los hechos, de mayor a menor; a igualdad de lo anterior
      gana la activacion con hechos declarados mas recientemente.
    Experta solo trae salience + recencia (DepthStrategy), la specificity se agrega aqui.
    """

    def get_key(self, activation):
        """Llave con la que se ordena la agenda (la mayor se ejecuta primero)."""
        salience = activation.rule.salience
        especificidad = len(activation.facts)
        recencia = sorted((f["__factid__"] for f in activation.facts), reverse=True)
        return (salience, especificidad, recencia)


class MotorEmparejamiento(ReglasEmparejamiento, KnowledgeEngine):
    """Motor de Experta con las reglas de emparejamiento."""

    __strategy__ = EstrategiaEmparejamiento

    def __init__(self, verbose=False):
        """verbose=True imprime cada regla al dispararse."""
        super().__init__()
        self.verbose = verbose
        self.disparos = []
        self.informe = {}

    def cargar(self, facts):
        """Reinicia el motor y declara los hechos iniciales en el orden recibido."""
        self.reset()
        self.disparos = []
        self.informe = {}
        for f in facts:
            self.declare(f)

    def recomendaciones(self):
        """Lista de Facts Recomendacion que hay en la memoria de trabajo."""
        return [f for f in self.facts.values() if isinstance(f, Recomendacion)]
