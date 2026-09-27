"""
Reglas del sistema experto de emparejamiento.

Niveles de prioridad (salience):
    ALTA = 100     descartes y creacion del puntaje
    DEPORTE = 60   deporte en comun (antes que el interes generico de R04)
    MEDIA = 50     deteccion de coincidencias y suma del puntaje
    BAJA = 10      decision final
    DEFECTO = -10  caso por defecto
    INFORME = -20  impresion del resultado con nombres y etiquetas

Todas las reglas de decision tienen NOT(Evaluado(a, b)): Evaluado es el lock-fact
que impide que un par reciba dos decisiones finales.
"""
import vocab as V
from experto.hechos import (Individuo, Relacion, Propiedad, Esquema, AfinidadDifusa,
                            Coincidencia, Puntaje, Recomendacion, Evaluado, LugarDescartado)
from experta import Rule, NOT, OR, TEST, MATCH, P, AS

ALTA, DEPORTE, MEDIA, BAJA, DEFECTO, INFORME = 100, 60, 50, 10, -10, -20


def es_numero(v):
    """Experta puede evaluar el P(...) de 'valor' antes de filtrar por predicado,
    asi que tambien le llegan textos (foaf:name, rdfs:label); se ignoran."""
    return isinstance(v, (int, float))


class ReglasEmparejamiento:
    """Mixin con las reglas. El motor (motor.py) hereda de esta clase."""

    def _log(self, regla, a, b, texto=""):
        """Guarda el orden de disparo y lo imprime si verbose esta activo."""
        self.disparos.append((regla, a, b))
        if self.verbose:
            print(f"[{regla}] {V.nombre_corto(a)}-{V.nombre_corto(b)} {texto}")

    def _decidir(self, regla, a, b, accion, motivo=""):
        """Declara la recomendacion final y el lock-fact Evaluado."""
        self._log(regla, a, b, f"-> {accion} {motivo}")
        self.declare(Recomendacion(a=a, b=b, accion=accion, motivo=motivo))
        self.declare(Evaluado(a=a, b=b))

    def _validado(self, tipo):
        """Cuenta un hecho que cumple el esquema (domain o subPropertyOf)."""
        self.validaciones[tipo] = self.validaciones.get(tipo, 0) + 1

    # ------------------------------------------------------------------
    # Prioridad ALTA: descartes
    # ------------------------------------------------------------------

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_BUSCA_OBJETIVO, objeto=MATCH.o1),
          Relacion(sujeto=MATCH.b, predicado=V.MT_BUSCA_OBJETIVO, objeto=MATCH.o2),
          Relacion(sujeto=MATCH.o1, predicado=V.MT_INCOMPATIBLE, objeto=MATCH.o2),
          NOT(Evaluado(a=MATCH.a, b=MATCH.b)),
          salience=ALTA)
    def r01_objetivos_incompatibles(self, a, b, o1, o2):
        """Descarta si buscan objetivos de relacion incompatibles."""
        self._decidir("R01", a, b, "descartar", "objetivos incompatibles")

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_PARTICIPA_EN, objeto=MATCH.c),
          Relacion(sujeto=MATCH.b, predicado=V.MT_PARTICIPA_EN, objeto=MATCH.c),
          Propiedad(sujeto=MATCH.c, predicado=V.MT_CALIFICACION, valor=P(lambda v: es_numero(v) and v <= 2)),
          NOT(Evaluado(a=MATCH.a, b=MATCH.b)),
          salience=ALTA)
    def r02_mala_cita_previa(self, a, b, c):
        """Descarta si ya tuvieron una cita juntos con calificacion <= 2."""
        self._decidir("R02", a, b, "descartar", "mala cita previa")

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Propiedad(sujeto=MATCH.x, predicado=V.MT_EDAD, valor=P(lambda v: es_numero(v) and v < 18)),
          TEST(lambda x, a, b: x in (a, b)),
          NOT(Evaluado(a=MATCH.a, b=MATCH.b)),
          salience=ALTA)
    def r21_menor_de_edad(self, a, b, x):
        """Descarta el par si alguno de los dos es menor de edad (edad < 18)."""
        self._decidir("R21", a, b, "descartar", "menor de edad")

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Individuo(uri=MATCH.a, tipo=V.MT_PERSONA),
          Individuo(uri=MATCH.b, tipo=V.MT_PERSONA),
          Individuo(uri=MATCH.a, tipo=V.FOAF_PERSON),
          Individuo(uri=MATCH.b, tipo=V.FOAF_PERSON),
          NOT(Puntaje(a=MATCH.a, b=MATCH.b)),
          salience=ALTA)
    def r03_iniciar_puntaje(self, a, b):
        """Crea el puntaje en 0 para cada par de personas.
        Ambos tipos (mt:Persona y foaf:Person) suelen venir del razonador."""
        self._log("R03", a, b)
        self.declare(Puntaje(a=a, b=b, valor=0))

    # ------------------------------------------------------------------
    # Prioridad MEDIA: coincidencias
    # ------------------------------------------------------------------

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_TIENE_INTERES, objeto=MATCH.x),
          Relacion(sujeto=MATCH.b, predicado=V.MT_TIENE_INTERES, objeto=MATCH.x),
          Individuo(uri=MATCH.x, tipo=V.MT_INTERES),
          NOT(Coincidencia(a=MATCH.a, b=MATCH.b, tipo="deporte", detalle=MATCH.x)),
          salience=MEDIA)
    def r04_interes_comun(self, a, b, x):
        """Interes compartido (incluye los inferidos desde practicaDeporte)."""
        self._log("R04", a, b, V.nombre_corto(x))
        self.declare(Coincidencia(a=a, b=b, tipo="interes", detalle=x))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_TIENE_VALOR, objeto=MATCH.v),
          Relacion(sujeto=MATCH.b, predicado=V.MT_TIENE_VALOR, objeto=MATCH.v),
          Individuo(uri=MATCH.v, tipo=V.MT_VALOR),
          salience=MEDIA)
    def r05_valor_comun(self, a, b, v):
        """Valor personal compartido."""
        self._log("R05", a, b, V.nombre_corto(v))
        self.declare(Coincidencia(a=a, b=b, tipo="valor", detalle=v))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_BUSCA_OBJETIVO, objeto=MATCH.o),
          Relacion(sujeto=MATCH.b, predicado=V.MT_BUSCA_OBJETIVO, objeto=MATCH.o),
          Individuo(uri=MATCH.o, tipo=V.MT_OBJETIVO),
          salience=MEDIA)
    def r06_mismo_objetivo(self, a, b, o):
        """Buscan el mismo tipo de relacion."""
        self._log("R06", a, b, V.nombre_corto(o))
        self.declare(Coincidencia(a=a, b=b, tipo="objetivo", detalle=o))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_VIVE_EN, objeto=MATCH.c),
          Relacion(sujeto=MATCH.b, predicado=V.MT_VIVE_EN, objeto=MATCH.c),
          Individuo(uri=MATCH.c, tipo=V.MT_CIUDAD),
          salience=MEDIA)
    def r07_misma_ciudad(self, a, b, c):
        """Viven en la misma ciudad."""
        self._log("R07", a, b, V.nombre_corto(c))
        self.declare(Coincidencia(a=a, b=b, tipo="ciudad", detalle=c))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_VIVE_EN, objeto=MATCH.c1),
          Relacion(sujeto=MATCH.b, predicado=V.MT_VIVE_EN, objeto=MATCH.c2),
          TEST(lambda c1, c2: c1 != c2),
          Relacion(sujeto=MATCH.c1, predicado=V.MT_UBICADO_EN, objeto=MATCH.r),
          Relacion(sujeto=MATCH.c2, predicado=V.MT_UBICADO_EN, objeto=MATCH.r),
          Individuo(uri=MATCH.r, tipo=V.MT_LUGAR),
          salience=MEDIA)
    def r07b_misma_region(self, a, b, c1, c2, r):
        """Ciudades distintas pero de la misma region."""
        self._log("R07b", a, b, V.nombre_corto(r))
        self.declare(Coincidencia(a=a, b=b, tipo="region", detalle=r))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_VIVE_EN, objeto=MATCH.c1),
          Relacion(sujeto=MATCH.b, predicado=V.MT_VIVE_EN, objeto=MATCH.c2),
          Relacion(sujeto=MATCH.c1, predicado=V.MT_UBICADO_EN, objeto=MATCH.r1),
          Relacion(sujeto=MATCH.c2, predicado=V.MT_UBICADO_EN, objeto=MATCH.r2),
          TEST(lambda r1, r2: r1 != r2),
          Relacion(sujeto=MATCH.r1, predicado=V.MT_UBICADO_EN, objeto=MATCH.d),
          Relacion(sujeto=MATCH.r2, predicado=V.MT_UBICADO_EN, objeto=MATCH.d),
          salience=MEDIA)
    def r07c_mismo_departamento(self, a, b, c1, c2, r1, r2, d):
        """Regiones distintas dentro del mismo lugar mayor (departamento)."""
        self._log("R07c", a, b, V.nombre_corto(d))
        self.declare(Coincidencia(a=a, b=b, tipo="departamento", detalle=d))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.FOAF_KNOWS, objeto=MATCH.c),
          Relacion(sujeto=MATCH.b, predicado=V.FOAF_KNOWS, objeto=MATCH.c),
          TEST(lambda a, b, c: c not in (a, b)),
          salience=MEDIA)
    def r08_amigo_comun(self, a, b, c):
        """Conocen a la misma persona (foaf:knows se infiere desde esAmigoDe)."""
        self._log("R08", a, b, V.nombre_corto(c))
        self.declare(Coincidencia(a=a, b=b, tipo="amigo_comun", detalle=c))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Individuo(uri=MATCH.a, tipo=MATCH.t),
          Individuo(uri=MATCH.b, tipo=MATCH.t),
          Esquema(sujeto=MATCH.t, relacion=V.SUBCLASE, objeto=V.MT_PERSONA),
          Esquema(sujeto=MATCH.t, relacion=V.TIPO, objeto=V.RDFS_CLASS),
          TEST(lambda t: t != V.MT_PERSONA),
          salience=MEDIA)
    def r09_misma_etapa(self, a, b, t):
        """Misma subclase de Persona (se lee del esquema, no esta fija en el codigo).
        Se exige ademas que t este declarada como rdfs:Class."""
        self._log("R09", a, b, V.nombre_corto(t))
        self.declare(Coincidencia(a=a, b=b, tipo="etapa", detalle=t))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b),
          Relacion(sujeto=MATCH.a, predicado=V.MT_PRACTICA_DEPORTE, objeto=MATCH.d),
          Relacion(sujeto=MATCH.b, predicado=V.MT_PRACTICA_DEPORTE, objeto=MATCH.d),
          Individuo(uri=MATCH.d, tipo=V.MT_DEPORTE),
          Individuo(uri=MATCH.d, tipo=V.MT_INTERES),
          salience=DEPORTE)
    def r10_deporte_comun(self, a, b, d):
        """Deporte en comun. Va en salience 60 para dispararse antes que R04: el
        deporte tambien es tieneInteres (subPropertyOf) y R04 lo salta con su NOT.
        Deporte es Interes por inferencia (subClassOf), por eso tambien se pide ese tipo."""
        self._log("R10", a, b, V.nombre_corto(d))
        self.declare(Coincidencia(a=a, b=b, tipo="deporte", detalle=d))

    @Rule(AS.c << Coincidencia(a=MATCH.a, b=MATCH.b, tipo=MATCH.t, contada=False),
          AS.p << Puntaje(a=MATCH.a, b=MATCH.b, valor=MATCH.v),
          salience=MEDIA)
    def r11_sumar_puntaje(self, c, p, a, b, t, v):
        """Suma la coincidencia al puntaje (+1, deporte +2).

        Esta regla modifica un hecho que esta en su propia condicion (Puntaje),
        asi que se marca contada=True para no volver a sumarla (anti-bucle).
        """
        puntos = 2 if t == "deporte" else 1
        self.modify(c, contada=True)
        self.modify(p, valor=v + puntos)
        self._log("R11", a, b, f"+{puntos} ({t}) = {v + puntos}")

    # ------------------------------------------------------------------
    # Prioridad BAJA: decision final
    # ------------------------------------------------------------------

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b, nivel="alta"),
          Puntaje(a=MATCH.a, b=MATCH.b, valor=P(lambda v: v >= 3)),
          Propiedad(sujeto=MATCH.a, predicado=V.MT_VERIFICADO, valor=True),
          Propiedad(sujeto=MATCH.b, predicado=V.MT_VERIFICADO, valor=True),
          NOT(Evaluado(a=MATCH.a, b=MATCH.b)),
          salience=BAJA)
    def r12_proponer_cita(self, a, b):
        """Compatibilidad alta, buen puntaje y ambos verificados (la mas especifica)."""
        self._decidir("R12", a, b, "proponer_cita")

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b, nivel=P(lambda n: n in ("media", "alta"))),
          Puntaje(a=MATCH.a, b=MATCH.b, valor=P(lambda v: v >= 2)),
          NOT(Evaluado(a=MATCH.a, b=MATCH.b)),
          salience=BAJA)
    def r13_sugerir_conversar(self, a, b):
        """Regla general: compatibilidad media o alta y puntaje de al menos 2."""
        self._decidir("R13", a, b, "sugerir_conversar")

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b, nivel="alta"),
          Puntaje(a=MATCH.a, b=MATCH.b),
          Propiedad(sujeto=MATCH.x, predicado=V.MT_VERIFICADO, valor=False),
          TEST(lambda x, a, b: x in (a, b)),
          NOT(Evaluado(a=MATCH.a, b=MATCH.b)),
          salience=BAJA)
    def r14_pedir_verificacion(self, a, b, x):
        """Compatibilidad alta pero alguno no tiene el perfil verificado."""
        self._decidir("R14", a, b, "pedir_verificacion", V.nombre_corto(x))

    @Rule(AfinidadDifusa(a=MATCH.a, b=MATCH.b, nivel="baja"),
          NOT(Evaluado(a=MATCH.a, b=MATCH.b)),
          salience=BAJA)
    def r15_compatibilidad_baja(self, a, b):
        """La logica difusa dio compatibilidad baja."""
        self._decidir("R15", a, b, "descartar", "compatibilidad baja")

    @Rule(Relacion(sujeto=MATCH.c, predicado=V.MT_OCURRIO_EN, objeto=MATCH.l),
          Individuo(uri=MATCH.c, tipo=V.MT_CITA),
          Propiedad(sujeto=MATCH.c, predicado=V.MT_CALIFICACION, valor=P(lambda v: es_numero(v) and v <= 2)),
          salience=MEDIA)
    def r16a_marcar_lugar(self, c, l):
        """Marca los lugares donde hubo una cita con calificacion <= 2."""
        self._log("R16a", l, c)
        self.declare(LugarDescartado(lugar=l, motivo=c))

    @Rule(Recomendacion(a=MATCH.a, b=MATCH.b, accion="proponer_cita"),
          Relacion(sujeto=MATCH.a, predicado=V.MT_VIVE_EN, objeto=MATCH.c),
          Relacion(sujeto=MATCH.b, predicado=V.MT_VIVE_EN, objeto=MATCH.c),
          Relacion(sujeto=MATCH.l, predicado=V.MT_UBICADO_EN, objeto=MATCH.c),
          Individuo(uri=MATCH.l, tipo=V.MT_LUGAR_CITA),
          NOT(LugarDescartado(lugar=MATCH.l)),
          NOT(Recomendacion(a=MATCH.a, b=MATCH.b, accion="sugerir_lugar")),
          salience=BAJA)
    def r16_sugerir_lugar(self, a, b, c, l):
        """Sugiere un lugar de la ciudad de ambos donde no haya habido citas malas."""
        self._log("R16", a, b, V.nombre_corto(l))
        self.declare(Recomendacion(a=a, b=b, accion="sugerir_lugar", motivo=l))

    @Rule(Puntaje(a=MATCH.a, b=MATCH.b),
          NOT(Evaluado(a=MATCH.a, b=MATCH.b)),
          salience=DEFECTO)
    def r17_revisar_manual(self, a, b):
        """Ninguna regla de decision aplico: queda para revision manual."""
        self._decidir("R17", a, b, "revisar_manual")

    # ------------------------------------------------------------------
    # Control de consistencia con el esquema y reporte
    # ------------------------------------------------------------------

    @Rule(Relacion(sujeto=MATCH.s, predicado=MATCH.p, objeto=MATCH.o),
          Esquema(sujeto=MATCH.p, relacion=V.RANGO, objeto=MATCH.c),
          NOT(Individuo(uri=MATCH.o, tipo=MATCH.c)),
          salience=ALTA)
    def r18_validar_rango(self, s, p, o, c):
        """Avisa si un objeto no es del tipo que pide el rango de la propiedad.
        Con el grafo razonado no deberia dispararse nunca."""
        print(f"[R18] Inconsistencia: {V.nombre_corto(o)} no es {V.nombre_corto(c)}")

    @Rule(OR(Relacion(sujeto=MATCH.s, predicado=MATCH.p),
             Propiedad(sujeto=MATCH.s, predicado=MATCH.p)),
          Esquema(sujeto=MATCH.p, relacion=V.DOMINIO, objeto=MATCH.c),
          Individuo(uri=MATCH.s, tipo=MATCH.c),
          salience=ALTA)
    def r22_dominio_valido(self, s, p, c):
        """Cuenta los hechos cuyo sujeto es del tipo que pide el dominio de la propiedad.
        Asi pasan por una regla edad, latitud, longitud y esAmigoDe, que las demas no leen."""
        self._validado("domain")

    @Rule(OR(Relacion(sujeto=MATCH.s, predicado=MATCH.p),
             Propiedad(sujeto=MATCH.s, predicado=MATCH.p)),
          Esquema(sujeto=MATCH.p, relacion=V.DOMINIO, objeto=MATCH.c),
          NOT(Individuo(uri=MATCH.s, tipo=MATCH.c)),
          salience=ALTA)
    def r22b_validar_dominio(self, s, p, c):
        """Avisa si el sujeto no es del tipo del dominio.
        Con el grafo razonado no deberia dispararse (rdfs2 ya le asigna el tipo)."""
        print(f"[R22b] Inconsistencia: {V.nombre_corto(s)} usa {V.nombre_corto(p)} "
              f"y no es {V.nombre_corto(c)}")

    @Rule(Relacion(sujeto=MATCH.s, predicado=MATCH.p, objeto=MATCH.o),
          Esquema(sujeto=MATCH.p, relacion=V.SUBPROPIEDAD, objeto=MATCH.q),
          TEST(lambda p, q: p != q),
          Esquema(sujeto=MATCH.p, relacion=V.TIPO, objeto=V.RDF_PROPERTY),
          Relacion(sujeto=MATCH.s, predicado=MATCH.q, objeto=MATCH.o),
          salience=ALTA)
    def r23_subpropiedad_valida(self, s, p, o, q):
        """Cuenta las relaciones de una subpropiedad (esAmigoDe, practicaDeporte) que
        tambien aparecen con su superpropiedad (foaf:knows, tieneInteres).
        El razonador agrega 'p subPropertyOf p' para toda propiedad; el TEST lo excluye."""
        self._validado("subPropertyOf")

    @Rule(Relacion(sujeto=MATCH.s, predicado=MATCH.p, objeto=MATCH.o),
          Esquema(sujeto=MATCH.p, relacion=V.SUBPROPIEDAD, objeto=MATCH.q),
          TEST(lambda p, q: p != q),
          Esquema(sujeto=MATCH.p, relacion=V.TIPO, objeto=V.RDF_PROPERTY),
          NOT(Relacion(sujeto=MATCH.s, predicado=MATCH.q, objeto=MATCH.o)),
          salience=ALTA)
    def r23b_validar_subpropiedad(self, s, p, o, q):
        """Avisa si falta la relacion con la superpropiedad.
        Con el grafo razonado no deberia dispararse (rdfs7 ya la agrega)."""
        print(f"[R23b] Inconsistencia: {V.nombre_corto(s)} {V.nombre_corto(p)} "
              f"{V.nombre_corto(o)} sin {V.nombre_corto(q)}")

    @Rule(Recomendacion(a=MATCH.a, b=MATCH.b, accion=MATCH.acc, motivo=MATCH.m),
          TEST(lambda acc: acc != "sugerir_lugar"),
          Propiedad(sujeto=MATCH.a, predicado=V.FOAF_NAME, valor=MATCH.na),
          Propiedad(sujeto=MATCH.b, predicado=V.FOAF_NAME, valor=MATCH.nb),
          salience=INFORME)
    def r19_informe(self, a, b, acc, m, na, nb):
        """Guarda el resultado del par con los nombres (foaf:name)."""
        self.informe.setdefault((a, b), {})["nombres"] = (na, nb)
        self.informe[(a, b)]["accion"] = acc
        self.informe[(a, b)]["motivo"] = m

    @Rule(Recomendacion(a=MATCH.a, b=MATCH.b, accion="sugerir_lugar", motivo=MATCH.l),
          Propiedad(sujeto=MATCH.l, predicado=V.RDFS_LABEL, valor=MATCH.etiqueta),
          salience=INFORME)
    def r20_informe_lugar(self, a, b, l, etiqueta):
        """Agrega al informe el lugar sugerido usando su rdfs:label."""
        self.informe.setdefault((a, b), {})["lugar"] = str(etiqueta)

    @Rule(Propiedad(sujeto=MATCH.x, predicado=V.RDFS_LABEL, valor=MATCH.etiqueta),
          salience=INFORME)
    def r24_glosario(self, x, etiqueta):
        """Arma el glosario con el rdfs:label de clases, propiedades e individuos."""
        self.glosario[x] = str(etiqueta)
