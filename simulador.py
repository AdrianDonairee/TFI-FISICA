"""
===============================================================================
Trabajo Final Integrador (TFI) - Física I
Opción A: Simulación de Tiro Parabólico con y sin Resistencia del Aire
Módulo: simulador.py
===============================================================================
Contiene el motor de simulación numérica, detección de eventos de impacto por
interpolación cúbica/raíces de SciPy, cálculo de magnitudes cinemáticas y métricas
clave (alcance máximo, altura máxima, tiempo de vuelo, velocidades y aceleraciones).
"""

from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np
from scipy.interpolate import CubicSpline
from scipy.optimize import root_scalar

from modelo import Proyectil


@dataclass
class ResultadoSimulacion:
    """
    Contenedor inmutable de datos cinemáticos y métricas de una simulación.
    """
    nombre: str
    t: np.ndarray
    x: np.ndarray
    y: np.ndarray
    vx: np.ndarray
    vy: np.ndarray
    v_mag: np.ndarray
    ax: np.ndarray
    ay: np.ndarray
    a_mag: np.ndarray
    
    # Métricas clave del movimiento
    alcance_maximo: float        # [m]
    altura_maxima: float         # [m]
    tiempo_altura_maxima: float  # [s]
    pos_x_altura_maxima: float   # [m]
    tiempo_vuelo: float          # [s]
    velocidad_impacto: float     # [m/s]
    angulo_impacto_deg: float    # [grados]


class SimuladorTiro:
    """
    Controlador encargado de orquestar la simulación de trayectorias físicas,
    tanto analíticas como numéricas, y de procesar sus métricas estadísticas.
    """

    def __init__(
        self,
        proyectil: Proyectil,
        v0: float = 65.0,
        angulo_grados: float = 45.0,
        x0: float = 0.0,
        y0: float = 0.0
    ) -> None:
        """
        Inicializa el simulador con las condiciones de contorno iniciales.

        Parámetros:
        -----------
        proyectil : Proyectil
            Instancia del modelo de proyectil.
        v0 : float
            Rapidez inicial de disparo en [m/s].
        angulo_grados : float
            Ángulo de elevación inicial en grados sexagesimales [°].
        x0 : float
            Posición inicial en el eje X [m].
        y0 : float
            Posición inicial en el eje Y [m] (altura de lanzamiento).
        """
        if v0 <= 0:
            raise ValueError("La rapidez inicial v0 debe ser estrictamente positiva.")
        if not (0.0 <= angulo_grados <= 90.0):
            raise ValueError("El ángulo de tiro debe pertenecer al intervalo [0°, 90°].")
        if y0 < 0:
            raise ValueError("La altura inicial y0 no puede ser negativa.")

        self.proyectil = proyectil
        self.v0 = float(v0)
        self.angulo_grados = float(angulo_grados)
        self.theta_rad = np.radians(self.angulo_grados)
        self.x0 = float(x0)
        self.y0 = float(y0)

        # Componentes iniciales de velocidad
        self.vx0 = self.v0 * np.cos(self.theta_rad)
        self.vy0 = self.v0 * np.sin(self.theta_rad)

    def simular_analitico_ideal(self, num_puntos: int = 1000) -> ResultadoSimulacion:
        """
        Calcula la trayectoria ideal (sin rozamiento) mediante soluciones analíticas exactas.
        """
        g = self.proyectil.gravedad
        # Tiempo de vuelo exacto: y0 + vy0*t - 0.5*g*t^2 = 0
        discriminante = self.vy0 ** 2 + 2 * g * self.y0
        t_vuelo = (self.vy0 + np.sqrt(discriminante)) / g

        t = np.linspace(0, t_vuelo, num_puntos)
        x, y, vx, vy, ax, ay = self.proyectil.solucion_analitica_ideal(
            t, self.x0, self.y0, self.v0, self.theta_rad
        )

        v_mag = np.hypot(vx, vy)
        a_mag = np.hypot(ax, ay)

        # Métricas analíticas exactas
        t_ymax = self.vy0 / g
        y_max = self.y0 + (self.vy0 ** 2) / (2 * g)
        x_ymax = self.x0 + self.vx0 * t_ymax
        alcance = self.x0 + self.vx0 * t_vuelo
        v_impacto = np.hypot(vx[-1], vy[-1])
        angulo_impacto = np.degrees(np.arctan2(np.abs(vy[-1]), vx[-1]))

        return ResultadoSimulacion(
            nombre="Ideal (Analítico)",
            t=t,
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            v_mag=v_mag,
            ax=ax,
            ay=ay,
            a_mag=a_mag,
            alcance_maximo=alcance,
            altura_maxima=y_max,
            tiempo_altura_maxima=t_ymax,
            pos_x_altura_maxima=x_ymax,
            tiempo_vuelo=t_vuelo,
            velocidad_impacto=v_impacto,
            angulo_impacto_deg=angulo_impacto
        )

    def simular_numerico(
        self,
        metodo: str = "rk4",
        con_resistencia: bool = True,
        dt: float = 0.001,
        t_max: float = 120.0
    ) -> ResultadoSimulacion:
        """
        Integra numéricamente las EDOs paso a paso hasta la detección exacta del impacto
        contra el suelo (y = 0) mediante interpolación cúbica (Splines) de alta precisión.

        Parámetros:
        -----------
        metodo : str
            'rk4' para Runge-Kutta 4to Orden, 'euler' para Euler hacia adelante.
        con_resistencia : bool
            True para modelo realista con resistencia aerodinámica cuadrática.
        dt : float
            Paso temporal de integración [s].
        t_max : float
            Límite superior de seguridad temporal [s].
        """
        if metodo.lower() not in ("rk4", "euler"):
            raise ValueError(f"Método numérico '{metodo}' no soportado. Use 'rk4' o 'euler'.")

        integrador = (
            self.proyectil.paso_rk4 if metodo.lower() == "rk4"
            else self.proyectil.paso_euler
        )

        # Estado inicial: [x, y, vx, vy]
        estado = np.array([self.x0, self.y0, self.vx0, self.vy0], dtype=float)
        t_actual = 0.0

        tiempos = [t_actual]
        estados = [estado.copy()]

        # Bucle de integración temporal
        while t_actual < t_max:
            estado_siguiente = integrador(t_actual, estado, dt, con_resistencia=con_resistencia)
            t_siguiente = t_actual + dt

            tiempos.append(t_siguiente)
            estados.append(estado_siguiente.copy())

            # Detectar si el proyectil cruzó el suelo (y <= 0)
            if estado_siguiente[1] <= 0.0 and len(tiempos) > 2:
                break

            estado = estado_siguiente
            t_actual = t_siguiente

        tiempos_arr = np.array(tiempos)
        estados_arr = np.array(estados)

        # --- Refinamiento de precisión del impacto con el suelo (y=0) ---
        spline_y = CubicSpline(tiempos_arr, estados_arr[:, 1])
        spline_x = CubicSpline(tiempos_arr, estados_arr[:, 0])
        spline_vx = CubicSpline(tiempos_arr, estados_arr[:, 2])
        spline_vy = CubicSpline(tiempos_arr, estados_arr[:, 3])

        # Raíz del impacto en el intervalo final
        t_izq = tiempos_arr[-2]
        t_der = tiempos_arr[-1]
        sol_raiz = root_scalar(spline_y, bracket=[t_izq, t_der], method="brentq")
        t_impacto = sol_raiz.root

        # Recortar y ajustar el array temporal para que termine exactamente en t_impacto
        tiempos_validos = tiempos_arr[tiempos_arr < t_impacto]
        tiempos_finales = np.append(tiempos_validos, t_impacto)

        x_final = spline_x(tiempos_finales)
        y_final = spline_y(tiempos_finales)
        y_final[-1] = 0.0  # Corrección exacta de cota en suelo

        vx_final = spline_vx(tiempos_finales)
        vy_final = spline_vy(tiempos_finales)
        v_mag = np.hypot(vx_final, vy_final)

        # Calcular aceleraciones instantáneas en toda la trayectoria
        ax_list = []
        ay_list = []
        for vx_val, vy_val in zip(vx_final, vy_final):
            ax_val, ay_val = self.proyectil.calcular_aceleraciones(
                vx_val, vy_val, con_resistencia=con_resistencia
            )
            ax_list.append(ax_val)
            ay_list.append(ay_val)

        ax_arr = np.array(ax_list)
        ay_arr = np.array(ay_list)
        a_mag = np.hypot(ax_arr, ay_arr)

        # Métricas clave
        idx_ymax = np.argmax(y_final)
        # Refinar altura máxima evaluando el cero de la derivada vy(t)=0
        try:
            raiz_vy = root_scalar(spline_vy, bracket=[tiempos_finales[0], tiempos_finales[-1]], method="brentq")
            t_ymax = raiz_vy.root
            y_max = float(spline_y(t_ymax))
            x_ymax = float(spline_x(t_ymax))
        except Exception:
            t_ymax = tiempos_finales[idx_ymax]
            y_max = y_final[idx_ymax]
            x_ymax = x_final[idx_ymax]

        alcance = x_final[-1]
        v_impacto = np.hypot(vx_final[-1], vy_final[-1])
        angulo_impacto = np.degrees(np.arctan2(np.abs(vy_final[-1]), vx_final[-1]))

        nombre_sim = (
            f"Real ({metodo.upper()} con Arrastre)" if con_resistencia
            else f"Ideal ({metodo.upper()} sin Arrastre)"
        )

        return ResultadoSimulacion(
            nombre=nombre_sim,
            t=tiempos_finales,
            x=x_final,
            y=y_final,
            vx=vx_final,
            vy=vy_final,
            v_mag=v_mag,
            ax=ax_arr,
            ay=ay_arr,
            a_mag=a_mag,
            alcance_maximo=alcance,
            altura_maxima=y_max,
            tiempo_altura_maxima=t_ymax,
            pos_x_altura_maxima=x_ymax,
            tiempo_vuelo=t_impacto,
            velocidad_impacto=v_impacto,
            angulo_impacto_deg=angulo_impacto
        )

    def ejecutar_estudio_completo(self, dt: float = 0.001) -> Dict[str, ResultadoSimulacion]:
        """
        Ejecuta los escenarios comparativos requeridos:
        1. Ideal (Solución Analítica Exacta)
        2. Ideal (Simulación Numérica RK4) -> Para validación de convergencia
        3. Real con Resistencia del Aire (Simulación Numérica RK4)
        4. Real con Resistencia del Aire (Simulación Numérica Euler)
        """
        res_analitico = self.simular_analitico_ideal()
        res_ideal_rk4 = self.simular_numerico(metodo="rk4", con_resistencia=False, dt=dt)
        res_real_rk4 = self.simular_numerico(metodo="rk4", con_resistencia=True, dt=dt)
        res_real_euler = self.simular_numerico(metodo="euler", con_resistencia=True, dt=dt)

        return {
            "ideal_analitico": res_analitico,
            "ideal_rk4": res_ideal_rk4,
            "real_rk4": res_real_rk4,
            "real_euler": res_real_euler
        }
