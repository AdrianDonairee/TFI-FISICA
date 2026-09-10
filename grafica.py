"""
===============================================================================
Trabajo Final Integrador (TFI) - Física I
Opción A: Simulación de Tiro Parabólico con y sin Resistencia del Aire
Módulo: grafica.py
===============================================================================
Generación de gráficos estáticos de alta calidad con Matplotlib:
1. Trayectoria 2D (y vs x) con puntos críticos destacados (vértice e impacto).
2. Cinemática completa (Posición vs t, Velocidad vs t, Aceleración vs t).
3. Comparativa de Fuerzas Aerodinámicas y Error Numérico.
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

    def graficar_cinematica_completa(
        self,
        resultados: Dict[str, ResultadoSimulacion],
        guardar_ruta: Optional[str] = None
    ) -> plt.Figure:
        """
        Genera un panel de 4 subgráficos comparando la cinemática detallada:
        1. Posición vs Tiempo: x(t) e y(t)
        2. Velocidad vs Tiempo: vx(t), vy(t) y magnitud total |v|(t)
        3. Aceleración vs Tiempo: ax(t), ay(t) y magnitud total |a|(t)
        4. Comparativa de Energía y Pérdida Numérica
        """
        fig, axes = plt.subplots(2, 2, figsize=(13, 9))

        res_ideal = resultados.get("ideal_analitico", resultados.get("ideal_rk4"))
        res_real = resultados["real_rk4"]

        color_ideal = "#1E88E5"
        color_real = "#D81B60"

        # --- Subgráfico 1: Posición vs Tiempo ---
        ax1 = axes[0, 0]
        ax1.plot(res_ideal.t, res_ideal.x, label="$x(t)$ Ideal", color=color_ideal, linestyle="--", lw=1.8)
        ax1.plot(res_ideal.t, res_ideal.y, label="$y(t)$ Ideal", color=color_ideal, linestyle=":", lw=2.0)
        ax1.plot(res_real.t, res_real.x, label="$x(t)$ Real", color=color_real, linestyle="-", lw=1.8)
        ax1.plot(res_real.t, res_real.y, label="$y(t)$ Real", color="#8E24AA", linestyle="-", lw=1.8)
        ax1.set_title("Posición vs Tiempo", fontweight="bold")
        ax1.set_xlabel("Tiempo $t$ [s]")
        ax1.set_ylabel("Posición [m]")
        ax1.grid(True, linestyle="--", alpha=0.6)
        ax1.legend(loc="upper left")

        # --- Subgráfico 2: Velocidad vs Tiempo ---
        ax2 = axes[0, 1]
        ax2.plot(res_ideal.t, res_ideal.vx, label="$v_x(t)$ Ideal", color=color_ideal, linestyle="--", lw=1.6)
        ax2.plot(res_ideal.t, res_ideal.vy, label="$v_y(t)$ Ideal", color=color_ideal, linestyle=":", lw=1.8)
        ax2.plot(res_ideal.t, res_ideal.v_mag, label="$|v(t)|$ Ideal", color="#0D47A1", linestyle="-.", lw=1.8)
        
        ax2.plot(res_real.t, res_real.vx, label="$v_x(t)$ Real", color=color_real, linestyle="-", lw=1.6)
        ax2.plot(res_real.t, res_real.vy, label="$v_y(t)$ Real", color="#8E24AA", linestyle="-", lw=1.8)
        ax2.plot(res_real.t, res_real.v_mag, label="$|v(t)|$ Real", color="#FF8F00", linestyle="-", lw=2.0)
        ax2.axhline(0, color="gray", lw=0.8, linestyle="--")
        ax2.set_title("Componentes y Magnitud de Velocidad vs Tiempo", fontweight="bold")
        ax2.set_xlabel("Tiempo $t$ [s]")
        ax2.set_ylabel("Velocidad [m/s]")
        ax2.grid(True, linestyle="--", alpha=0.6)
        ax2.legend(loc="upper right")

        # --- Subgráfico 3: Aceleración vs Tiempo ---
        ax3 = axes[1, 0]
        ax3.plot(res_ideal.t, res_ideal.ax, label="$a_x(t)$ Ideal (0)", color=color_ideal, linestyle="--", lw=1.6)
        ax3.plot(res_ideal.t, res_ideal.ay, label="$a_y(t)$ Ideal ($-g$)", color=color_ideal, linestyle=":", lw=1.8)
        
        ax3.plot(res_real.t, res_real.ax, label="$a_x(t)$ Real (Arrastre)", color=color_real, linestyle="-", lw=1.8)
        ax3.plot(res_real.t, res_real.ay, label="$a_y(t)$ Real", color="#8E24AA", linestyle="-", lw=1.8)
        ax3.plot(res_real.t, res_real.a_mag, label="$|a(t)|$ Real", color="#00897B", linestyle="-", lw=2.0)
        ax3.set_title("Componentes y Magnitud de Aceleración vs Tiempo", fontweight="bold")
        ax3.set_xlabel("Tiempo $t$ [s]")
        ax3.set_ylabel("Aceleración [m/s$^2$]")
        ax3.grid(True, linestyle="--", alpha=0.6)
        ax3.legend(loc="upper right")

        # --- Subgráfico 4: Análisis del Error Numérico (RK4 vs Analítico) ---
        ax4 = axes[1, 1]
        res_rk4_ideal = resultados.get("ideal_rk4")
        if res_rk4_ideal and res_ideal:
            # Interpolar para comparar mismos instantes
            t_comun = np.linspace(0, min(res_ideal.tiempo_vuelo, res_rk4_ideal.tiempo_vuelo), 500)
            y_analitico_interp = np.interp(t_comun, res_ideal.t, res_ideal.y)
            y_rk4_interp = np.interp(t_comun, res_rk4_ideal.t, res_rk4_ideal.y)
            error_y = np.abs(y_analitico_interp - y_rk4_interp)

            ax4.plot(t_comun, error_y, color="#2E7D32", lw=2.0, label="Error Absoluto $|y_{analitica} - y_{RK4}|$")
            ax4.set_title("Validación Numérica: Error Absoluto de Integración RK4", fontweight="bold")
            ax4.set_xlabel("Tiempo $t$ [s]")
            ax4.set_ylabel("Error en $y$ [m]")
            ax4.set_yscale("log")
            ax4.grid(True, which="both", linestyle="--", alpha=0.6)
            ax4.legend(loc="upper left")

        plt.suptitle("Estudio Cinemático y Dinámico Integral del Proyectil", fontsize=15, fontweight="bold", y=0.99)
        plt.tight_layout()

        if guardar_ruta:
            fig.savefig(guardar_ruta, dpi=300)
        return fig

    @staticmethod
    def mostrar():
        """Despliega todas las figuras activas de matplotlib."""
        plt.show()
