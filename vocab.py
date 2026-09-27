"""
Constantes con los nombres del dominio de emparejamiento.

Las usan el sistema experto, la preparación del difuso y el main.
El traductor NO importa este archivo, para que no dependa del dominio.
"""

MT = "http://ejemplo.org/emparejamiento#"
FOAF = "http://xmlns.com/foaf/0.1/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
RDF = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

# Clases
MT_PERSONA = MT + "Persona"
MT_ESTUDIANTE = MT + "Estudiante"
MT_PROFESIONAL = MT + "Profesional"
MT_INTERES = MT + "Interes"
MT_DEPORTE = MT + "Deporte"
MT_VALOR = MT + "Valor"
MT_OBJETIVO = MT + "ObjetivoRelacion"
MT_LUGAR = MT + "Lugar"
MT_CIUDAD = MT + "Ciudad"
MT_LUGAR_CITA = MT + "LugarDeCita"
MT_CITA = MT + "Cita"

# Propiedades
MT_TIENE_INTERES = MT + "tieneInteres"
MT_PRACTICA_DEPORTE = MT + "practicaDeporte"
MT_TIENE_VALOR = MT + "tieneValor"
MT_BUSCA_OBJETIVO = MT + "buscaObjetivo"
MT_INCOMPATIBLE = MT + "esIncompatibleCon"
MT_VIVE_EN = MT + "viveEn"
MT_AMIGO_DE = MT + "esAmigoDe"
MT_PARTICIPA_EN = MT + "participaEn"
MT_OCURRIO_EN = MT + "ocurrioEn"
MT_UBICADO_EN = MT + "ubicadoEn"
MT_EDAD = MT + "edad"
MT_CALIFICACION = MT + "calificacion"
MT_LATITUD = MT + "latitud"
MT_LONGITUD = MT + "longitud"
MT_VERIFICADO = MT + "perfilVerificado"

FOAF_PERSON = FOAF + "Person"
FOAF_NAME = FOAF + "name"
FOAF_KNOWS = FOAF + "knows"
RDFS_LABEL = RDFS + "label"
RDFS_CLASS = RDFS + "Class"
RDF_PROPERTY = RDF + "Property"

# Relaciones de esquema (campo 'relacion' del Fact Esquema)
SUBCLASE = "subClassOf"
SUBPROPIEDAD = "subPropertyOf"
DOMINIO = "domain"
RANGO = "range"
TIPO = "tipo"


def nombre_corto(uri):
    """Devuelve la parte final de un URI (lo que va despues de # o /)."""
    return uri.split("#")[-1].split("/")[-1]
