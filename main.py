"""
Sistema hibrido de emparejamiento: Ontologia + Logica difusa + Sistema experto.

Flujo:
    1. Se carga el .ttl y se razona con DeductiveClosure(RDFS_Semantics).
    2. El traductor convierte todo el grafo inferido en Facts.
    3. Para cada par de personas se calcula la compatibilidad difusa.
    4. El motor experto recibe los Facts + AfinidadDifusa y decide.

Uso:  python main.py [ruta_ttl]
"""
import os
import sys

import vocab as V
from ontologia.razonamiento import cargar_y_razonar, mostrar_razonamiento
from integracion.traductor import traducir, resumen
from integracion.preparar_difuso import calcular_pares
from experto.hechos import Individuo
from experto.motor import MotorEmparejamiento

BASE = os.path.dirname(os.path.abspath(__file__))
RUTA_TTL = os.path.join(BASE, "ontologia", "emparejamiento.ttl")


def titulo(texto):
    """Imprime un encabezado de seccion."""
    print("\n" + "=" * 70 + f"\n{texto}\n" + "=" * 70)


def ejecutar(ruta_ttl=RUTA_TTL, pares_traza=(("Andres", "Sofia"), ("Mateo", "Sofia"))):
    """Corre todo el sistema y devuelve el motor ya ejecutado."""
    titulo("1. ONTOLOGIA Y RAZONAMIENTO RDFS")
    g_original, g_inferido = cargar_y_razonar(ruta_ttl)
    mostrar_razonamiento(g_original, g_inferido)

    titulo("2. TRADUCTOR ONTOLOGIA -> HECHOS")
    facts = traducir(g_inferido, g_original)
    print(f"Hechos generados: {len(facts)}")
    for clase, (total, inferidos) in resumen(facts).items():
        print(f"   {clase:<10} {total:>4}  (inferidos: {inferidos})")
    print("Personas encontradas y sus tipos:")
    tipos = {}
    for f in facts:
        if isinstance(f, Individuo):
            tipos.setdefault(f["uri"], []).append(f"{V.nombre_corto(f['tipo'])} ({f['origen']})")
    for uri in sorted(tipos):
        if any(t.startswith("Persona ") for t in tipos[uri]):
            print(f"   {V.nombre_corto(uri):<10} " + ", ".join(sorted(tipos[uri])))

    titulo("3. LOGICA DIFUSA POR PAR")
    afinidades = calcular_pares(facts)
    print(f"{'par':<20}{'edad':>6}{'afin%':>8}{'km':>8}{'score':>8}  nivel")
    for af in afinidades:
        par = f"{V.nombre_corto(af['a'])}-{V.nombre_corto(af['b'])}"
        print(f"{par:<20}{af['edad_diff']:>6.0f}{af['afinidad']:>8.1f}"
              f"{af['distancia_km']:>8.1f}{af['score']:>8.1f}  {af['nivel']}")

    titulo("4. SISTEMA EXPERTO")
    motor = MotorEmparejamiento()
    motor.cargar(facts + afinidades)
    motor.run()

    print("Primeros disparos del motor (a igual salience y specificity gana el hecho mas reciente):")
    for regla, x, y in motor.disparos[:8]:
        print(f"   {regla} {V.nombre_corto(x)}-{V.nombre_corto(y)}")

    for a, b in pares_traza:
        ua, ub = V.MT + a, V.MT + b
        print(f"\nOrden de disparo para {a}-{b}:")
        for regla, x, y in motor.disparos:
            if (x, y) == (ua, ub):
                print(f"   {regla}", end="")
        print()

    # se recorren los Facts Recomendacion; el informe (R19/R20) solo aporta nombres
    print("\nRecomendaciones:")
    lugares = {(r["a"], r["b"]): r["motivo"] for r in motor.recomendaciones()
               if r["accion"] == "sugerir_lugar"}
    conteo = {}
    for r in sorted(motor.recomendaciones(), key=lambda f: (f["a"], f["b"])):
        if r["accion"] == "sugerir_lugar":
            continue
        a, b = r["a"], r["b"]
        info = motor.informe.get((a, b), {})
        na, nb = info.get("nombres", (V.nombre_corto(a), V.nombre_corto(b)))
        linea = f"   {na + ' - ' + nb:<22} {r['accion']:<20} {r['motivo']}"
        if (a, b) in lugares:
            linea += f"  lugar sugerido: {info.get('lugar', V.nombre_corto(lugares[(a, b)]))}"
        print(linea)
        conteo[r["accion"]] = conteo.get(r["accion"], 0) + 1

    print(f"\nTotal de pares: {sum(conteo.values())}  {conteo}")
    return motor


if __name__ == "__main__":
    ejecutar(sys.argv[1] if len(sys.argv) > 1 else RUTA_TTL)
