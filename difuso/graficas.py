"""
Graficas de las funciones de pertenencia (incluye los modificadores).
"""
import os

import matplotlib
import matplotlib.pyplot as plt

from difuso.variables import crear_variables


def graficar_funciones(carpeta="docs", mostrar=False):
    """Dibuja cada variable en un subplot y guarda la imagen en 'carpeta'."""
    variables = crear_variables()
    fig, ejes = plt.subplots(2, 2, figsize=(12, 8))
    for var, ax in zip(variables, ejes.flat):
        for nombre, termino in var.terms.items():
            estilo = "--" if nombre.startswith(("muy", "ligeramente")) else "-"
            ax.plot(var.universe, termino.mf, estilo, label=nombre)
        ax.set_title(var.label)
        ax.set_ylabel("pertenencia")
        ax.set_ylim(-0.05, 1.05)
        ax.legend(fontsize=8)
        ax.grid(alpha=0.3)
    fig.tight_layout()
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "funciones_pertenencia.png")
    fig.savefig(ruta, dpi=120)
    if mostrar:
        plt.show()
    plt.close(fig)
    return ruta


if __name__ == "__main__":
    matplotlib.use("Agg")
    print(graficar_funciones())
