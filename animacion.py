"""
===============================================================================
Trabajo Final Integrador (TFI) - Física I
Opción A: Simulación de Tiro Parabólico con y sin Resistencia del Aire
Módulo: animacion.py
===============================================================================
Módulo de visualización dinámica en tiempo real utilizando
matplotlib.animation.FuncAnimation. Proporciona una simulación visual fluida
en 2D con renderizado sincronizado, estela de trayectoria y HUD de telemetría.
"""

from typing import Dict, Optional
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np

from simulador import ResultadoSimulacion


class AnimadorProyectil:
    """
    Controla la animación 2D en tiempo real comparativa de los dos proyectiles.
    """

    def __init__(
        self,
        resultados: Dict[str, ResultadoSimulacion],
        fps: int = 60,
        factor_velocidad: float = 1.0
    ) -> None:
        """
        Inicializa el animador con los resultados cinemáticos.

        Parámetros:
        -----------
        resultados : dict
            Diccionario con las simulaciones obtenidas de SimuladorTiro.
        fps : int
            Cuadros por segundo deseados de la animación.
        factor_velocidad : float
            Velocidad de reproducción (1.0 = tiempo real, 0.5 = cámara lenta).
        """
        self.res_ideal = resultados.get("ideal_analitico", resultados.get("ideal_rk4"))
        self.res_real = resultados["real_rk4"]
        self.fps = fps
        self.factor_velocidad = factor_velocidad

        # Construir base de tiempo común sincronizada para el renderizado
        t_max_total = max(self.res_ideal.tiempo_vuelo, self.res_real.tiempo_vuelo)
        self.num_frames = int(t_max_total * self.fps / self.factor_velocidad)
        self.t_anim = np.linspace(0, t_max_total, self.num_frames)

        # Interpolar estados en la escala de tiempo común
        self.x_ideal = np.interp(self.t_anim, self.res_ideal.t, self.res_ideal.x)
        self.y_ideal = np.interp(self.t_anim, self.res_ideal.t, self.res_ideal.y)
        self.v_ideal = np.interp(self.t_anim, self.res_ideal.t, self.res_ideal.v_mag)
        self.a_ideal = np.interp(self.t_anim, self.res_ideal.t, self.res_ideal.a_mag)

        self.x_real = np.interp(self.t_anim, self.res_real.t, self.res_real.x)
        self.y_real = np.interp(self.t_anim, self.res_real.t, self.res_real.y)
        self.v_real = np.interp(self.t_anim, self.res_real.t, self.res_real.v_mag)
        self.a_real = np.interp(self.t_anim, self.res_real.t, self.res_real.a_mag)

        # Congelar proyectiles cuando tocan el suelo (t > t_vuelo)
        idx_fin_ideal = self.t_anim >= self.res_ideal.tiempo_vuelo
        self.x_ideal[idx_fin_ideal] = self.res_ideal.alcance_maximo
        self.y_ideal[idx_fin_ideal] = 0.0
        self.v_ideal[idx_fin_ideal] = 0.0
        self.a_ideal[idx_fin_ideal] = 0.0

        idx_fin_real = self.t_anim >= self.res_real.tiempo_vuelo
        self.x_real[idx_fin_real] = self.res_real.alcance_maximo
        self.y_real[idx_fin_real] = 0.0
        self.v_real[idx_fin_real] = 0.0
        self.a_real[idx_fin_real] = 0.0

        self.fig, self.ax = plt.subplots(figsize=(11, 6.5))
        self.anim = None

    def _inicializar_grafico(self):
        """Configura los límites fijos, fondos y elementos visuales estáticos."""
        self.ax.clear()
        
        min_x = min(0.0, float(np.min(self.x_ideal)), float(np.min(self.x_real)))
        max_x = max(float(np.max(self.x_ideal)), float(np.max(self.x_real)), self.res_ideal.alcance_maximo, self.res_real.alcance_maximo) * 1.08
        max_y = max(self.res_ideal.altura_maxima, self.res_real.altura_maxima) * 1.25

        self.ax.set_xlim(min(min_x - 2, -2), max(max_x, 10.0))
        self.ax.set_ylim(-2, max(max_y, 5.0))
        self.ax.set_xlabel("Distancia Horizontal $x$ [m]", fontsize=11, fontweight="bold")
        self.ax.set_ylabel("Altura Vertical $y$ [m]", fontsize=11, fontweight="bold")
        self.ax.set_title("Animación Dinámica del Vuelo: Trayectoria Ideal vs Real", fontsize=13, fontweight="bold", pad=12)
        
        # Suelo
        self.ax.axhline(0, color="#37474F", linewidth=2.0, zorder=2)
        self.ax.fill_between([min(min_x - 5, -5), max(max_x + 10, 20.0)], [-5, -5], [0, 0], color="#ECEFF1", zorder=1)
        self.ax.grid(True, linestyle="--", alpha=0.5)

        # Elementos dinámicos a actualizar en cada frame
        self.linea_ideal, = self.ax.plot([], [], color="#1E88E5", linestyle="--", lw=1.8, label="Ideal (Sin Arrastre)")
        self.linea_real, = self.ax.plot([], [], color="#D81B60", linestyle="-", lw=2.2, label="Real (Arrastre Cuadrático)")
        
        self.punto_ideal, = self.ax.plot([], [], marker="o", markersize=10, color="#0D47A1", zorder=6)
        self.punto_real, = self.ax.plot([], [], marker="o", markersize=10, color="#880E4F", zorder=6)

        # Panel HUD (Heads-Up Display) de telemetría
        self.hud_texto = self.ax.text(
            0.02, 0.95, "", transform=self.ax.transAxes,
            verticalalignment="top", fontsize=9.5, fontfamily="monospace",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#FAFAFA", edgecolor="#BDBDBD", alpha=0.92)
        )

        self.ax.legend(loc="upper right", frameon=True, facecolor="white", edgecolor="#BDBDBD")
        return self.linea_ideal, self.linea_real, self.punto_ideal, self.punto_real, self.hud_texto

    def _actualizar_frame(self, frame: int):
        """Actualiza la posición de los proyectiles y la telemetría en el frame actual."""
        t_actual = self.t_anim[frame]

        # Actualizar líneas de recorrido
        self.linea_ideal.set_data(self.x_ideal[:frame + 1], self.y_ideal[:frame + 1])
        self.linea_real.set_data(self.x_real[:frame + 1], self.y_real[:frame + 1])

        # Actualizar puntos (cabezas de proyectil)
        self.punto_ideal.set_data([self.x_ideal[frame]], [self.y_ideal[frame]])
        self.punto_real.set_data([self.x_real[frame]], [self.y_real[frame]])

        # Telemetría en tiempo real
        hud_info = (
            f"⏱️ Tiempo: {t_actual:5.2f} s\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔵 IDEAL (Sin Aire):\n"
            f"   Posición:     ({self.x_ideal[frame]:6.1f} m, {self.y_ideal[frame]:5.1f} m)\n"
            f"   Velocidad |v|: {self.v_ideal[frame]:5.1f} m/s\n"
            f"   Acelerac. |a|: {self.a_ideal[frame]:5.2f} m/s²\n"
            f"────────────────────────────────────\n"
            f"🔴 REAL (Con Arrastre RK4):\n"
            f"   Posición:     ({self.x_real[frame]:6.1f} m, {self.y_real[frame]:5.1f} m)\n"
            f"   Velocidad |v|: {self.v_real[frame]:5.1f} m/s\n"
            f"   Acelerac. |a|: {self.a_real[frame]:5.2f} m/s²"
        )
        self.hud_texto.set_text(hud_info)

        return self.linea_ideal, self.linea_real, self.punto_ideal, self.punto_real, self.hud_texto

    def iniciar(self, guardar_gif: Optional[str] = None):
        """
        Ejecuta la animación interactiva de Matplotlib.
        """
        intervalo_ms = 1000 / self.fps

        self.anim = animation.FuncAnimation(
            self.fig,
            self._actualizar_frame,
            init_func=self._inicializar_grafico,
            frames=self.num_frames,
            interval=intervalo_ms,
            blit=True,
            repeat=True,
            repeat_delay=1500
        )

        plt.tight_layout()

        if guardar_gif:
            print(f"Guardando animación en '{guardar_gif}'...")
            self.anim.save(guardar_gif, writer="pillow", fps=self.fps)
            print("Animación guardada exitosamente.")

        plt.show()
