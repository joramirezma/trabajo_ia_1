"""
Clases de hechos del sistema experto.
"""
import collections
import collections.abc

# experta usa collections.Mapping, que ya no existe en Python >= 3.10
for _n in ("Mapping", "MutableMapping", "Iterable", "Callable", "Sequence"):
    if not hasattr(collections, _n):
        setattr(collections, _n, getattr(collections.abc, _n))

from experta import Fact, Field  # noqa: E402


# --- Producidos por el traductor ---

class Individuo(Fact):
    """uri es de tipo 'tipo' (triple rdf:type). origen: asertado | inferido."""
    uri = Field(str, mandatory=True)
    tipo = Field(str, mandatory=True)
    origen = Field(str, default="asertado")


class Relacion(Fact):
    """Triple cuyo objeto es otro recurso (URI)."""
    sujeto = Field(str, mandatory=True)
    predicado = Field(str, mandatory=True)
    objeto = Field(str, mandatory=True)
    origen = Field(str, default="asertado")


class Propiedad(Fact):
    """Triple cuyo objeto es un literal. valor ya viene convertido a tipo Python."""
    sujeto = Field(str, mandatory=True)
    predicado = Field(str, mandatory=True)
    valor = Field(object, mandatory=True)
    datatype = Field(str, default="")


class Esquema(Fact):
    """Axioma del esquema: subClassOf, subPropertyOf, domain o range."""
    sujeto = Field(str, mandatory=True)
    relacion = Field(str, mandatory=True)
    objeto = Field(str, mandatory=True)


# --- Producido con la logica difusa ---

class AfinidadDifusa(Fact):
    """Resultado difuso para el par (a, b), con a < b."""
    a = Field(str, mandatory=True)
    b = Field(str, mandatory=True)
    edad_diff = Field(float)
    afinidad = Field(float)
    distancia_km = Field(float)
    score = Field(float)
    nivel = Field(str)


# --- Producidos por las reglas ---

class Coincidencia(Fact):
    """Algo que el par tiene en comun. contada evita sumarla dos veces."""
    a = Field(str)
    b = Field(str)
    tipo = Field(str)
    detalle = Field(str)
    contada = Field(bool, default=False)


class Puntaje(Fact):
    """Suma de coincidencias del par."""
    a = Field(str)
    b = Field(str)
    valor = Field(int, default=0)


class Recomendacion(Fact):
    """Accion recomendada para el par."""
    a = Field(str)
    b = Field(str)
    accion = Field(str)
    motivo = Field(str, default="")


class LugarDescartado(Fact):
    """Lugar de cita donde hubo una cita mal calificada."""
    lugar = Field(str)
    motivo = Field(str, default="")


class Evaluado(Fact):
    """Lock-fact: el par ya tiene decision final."""
    a = Field(str)
    b = Field(str)
