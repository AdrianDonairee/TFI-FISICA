"""
===============================================================================
Trabajo Final Integrador (TFI) - Física I
Opción A: Simulación de Tiro Parabólico con y sin Resistencia del Aire
Módulo: grafica.py
===============================================================================
Generación de gráficos estáticos de alta calidad con Matplotlib:
1. Trayectoria 2D (y vs x) con puntos críticos destacados (vértice e impacto).
"""

from typing import Dict, Optional
import matplotlib.pyplot as plt
import numpy as np

from simulador import ResultadoSimulacion


class GraficadorTrayectoria:
    """
    Gestiona la visualización gráfica estática de los resultados cinemáticos y dinámicos.
    """

    def __init__(self, estilo: str = "seaborn-v0_8-whitegrid") -> None:
        """
        Configura el estilo y parámetros tipográficos para publicaciones científicas.
        """
        try:
            plt.style.use(estilo)
        except Exception:
            plt.style.use("default")

        # Configuración estética general
        plt.rcParams.update({
            "font.family": "sans-serif",
            "font.size": 10,
            "axes.labelsize": 11,
            "axes.titlesize": 12,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "figure.titlesize": 14,
            "figure.dpi": 120
        })

    def graficar_trayectoria_2d(
        self,
        resultados: Dict[str, ResultadoSimulacion],
        guardar_ruta: Optional[str] = None
    ) -> plt.Figure:
        """
        Genera el gráfico comparativo de la trayectoria en el plano XY (y vs x).
        Resalta el alcance máximo y la altura máxima para cada modelo.
        """
        fig, ax = plt.subplots(figsize=(10, 6))

        res_ideal = resultados.get("ideal_analitico", resultados.get("ideal_rk4"))
        res_real = resultados["real_rk4"]

        # 1. Curva Ideal
        if res_ideal:
            ax.plot(
                res_ideal.x, res_ideal.y,
                color="#1E88E5", linestyle="--", linewidth=2.2,
                label=f"Ideal (Sin Rozamiento) - Alcance: {res_ideal.alcance_maximo:.2f} m"
            )
            # Altura máxima ideal
            ax.scatter(
                [res_ideal.pos_x_altura_maxima], [res_ideal.altura_maxima],
                color="#0D47A1", s=70, zorder=5
            )
            ax.annotate(
                f"H. Máx Ideal: {res_ideal.altura_maxima:.2f} m\n(x = {res_ideal.pos_x_altura_maxima:.1f} m)",
                xy=(res_ideal.pos_x_altura_maxima, res_ideal.altura_maxima),
                xytext=(res_ideal.pos_x_altura_maxima - 10, res_ideal.altura_maxima + (res_ideal.altura_maxima * 0.05)),
                arrowprops=dict(facecolor="#0D47A1", arrowstyle="->", lw=1.2),
                fontsize=8.5, fontweight="bold", color="#0D47A1",
                bbox=dict(boxstyle="round,pad=0.3", fc="#E3F2FD", ec="#1E88E5", alpha=0.9)
            )

        # 2. Curva Real con Resistencia
        ax.plot(
            res_real.x, res_real.y,
            color="#D81B60", linestyle="-", linewidth=2.4,
            label=f"Real (Arrastre Cuadrático RK4) - Alcance: {res_real.alcance_maximo:.2f} m"
        )
        # Altura máxima real
        ax.scatter(
            [res_real.pos_x_altura_maxima], [res_real.altura_maxima],
            color="#880E4F", s=70, zorder=5
        )
        ax.annotate(
            f"H. Máx Real: {res_real.altura_maxima:.2f} m\n(x = {res_real.pos_x_altura_maxima:.1f} m)",
            xy=(res_real.pos_x_altura_maxima, res_real.altura_maxima),
            xytext=(res_real.pos_x_altura_maxima + 5, res_real.altura_maxima * 0.75),
            arrowprops=dict(facecolor="#880E4F", arrowstyle="->", lw=1.2),
            fontsize=8.5, fontweight="bold", color="#880E4F",
            bbox=dict(boxstyle="round,pad=0.3", fc="#FCE4EC", ec="#D81B60", alpha=0.9)
        )

        # 3. Puntos de Impacto
        if res_ideal:
            ax.scatter([res_ideal.alcance_maximo], [0], color="#1E88E5", s=60, marker="X", zorder=5)
        ax.scatter([res_real.alcance_maximo], [0], color="#D81B60", s=60, marker="X", zorder=5)

        # Área sombreada entre curvas para destacar la variación por arrastre
        if res_ideal:
            min_alcance = min(res_ideal.alcance_maximo, res_real.alcance_maximo)
            if min_alcance > 0:
                x_interp = np.linspace(0, min_alcance, 300)
                y_ideal_interp = np.interp(x_interp, res_ideal.x, res_ideal.y)
                y_real_interp = np.interp(x_interp, res_real.x, res_real.y)
                ax.fill_between(x_interp, y_ideal_interp, y_real_interp, color="#FFC107", alpha=0.18, label="Pérdida por Arrastre")

        # Ajustes de ejes y detalles visuales
        ax.axhline(0, color="black", linewidth=1.2, linestyle="-")
        ax.set_title("Comparación de Trayectorias 2D: Tiro Ideal vs Tiro Real con Resistencia del Aire", pad=12, fontweight="bold")
        ax.set_xlabel("Distancia Horizontal $x$ [m]")
        ax.set_ylabel("Altura Vertical $y$ [m]")

        min_x = min(0.0, float(np.min(res_real.x)), float(np.min(res_ideal.x)) if res_ideal else 0.0)
        max_x = max(float(np.max(res_real.x)), float(np.max(res_ideal.x)) if res_ideal else 0.0) * 1.08
        max_y = max(res_ideal.altura_maxima if res_ideal else 0.0, res_real.altura_maxima) * 1.25

        ax.set_xlim(left=min(min_x - 2, -2), right=max(max_x, 10.0))
        ax.set_ylim(bottom=-1, top=max(max_y, 5.0))
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(loc="upper right", frameon=True, shadow=True)

        plt.tight_layout()
        if guardar_ruta:
            fig.savefig(guardar_ruta, dpi=300)
        return fig

    @staticmethod
    def mostrar():
        """Despliega todas las figuras activas de matplotlib."""
        plt.show()
