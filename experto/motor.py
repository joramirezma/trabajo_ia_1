"""
Motor de inferencia y estrategia de resolucion de conflictos.

Se usa la estrategia por defecto de Experta (DepthStrategy). Cada activacion
se ordena con la llave

    (salience, [factid_1, factid_2, ..., factid_n])

con los factid ordenados de mayor a menor; la mayor llave se ejecuta primero.
    - salience: prioridad declarada en la regla (primer elemento).
    - recencia: si la salience es igual se comparan los factid uno a uno;
      gana la activacion con hechos declarados mas recientemente.
    - specificity: si todos los factid comparados son iguales y una lista se
      acaba antes, gana la lista mas larga (la regla que empareja mas hechos).
Las dos ultimas salen de la comparacion lexicografica de listas de Python.
"""
from experto.hechos import Recomendacion  # importa primero: aplica el parche de collections
from experta import KnowledgeEngine

from experto.reglas import ReglasEmparejamiento


class MotorEmparejamiento(ReglasEmparejamiento, KnowledgeEngine):
    """Motor de Experta con las reglas de emparejamiento (estrategia por defecto)."""

    def __init__(self, verbose=False):
        """verbose=True imprime cada regla al dispararse."""
        super().__init__()
        self.verbose = verbose
        self.disparos = []
        self.informe = {}
        self.validaciones = {}
        self.glosario = {}

    def cargar(self, facts):
        """Reinicia el motor y declara los hechos iniciales en el orden recibido."""
        self.reset()
        self.disparos = []
        self.informe = {}
        self.validaciones = {}
        self.glosario = {}
        for f in facts:
            self.declare(f)

    def recomendaciones(self):
        """Lista de Facts Recomendacion que hay en la memoria de trabajo."""
        return [f for f in self.facts.values() if isinstance(f, Recomendacion)]
