"""
===============================================================================
Trabajo Final Integrador (TFI) - Física I
Opción A: Simulación de Tiro Parabólico con y sin Resistencia del Aire
Módulo: modelo.py
===============================================================================
Define la modelación física orientada a objetos (POO), propiedades del proyectil,
dinámica de fuerzas aerodinámicas (arrastre cuadrático) e integradores numéricos
(Runge-Kutta de 4to Orden y Método de Euler).
"""

from typing import Tuple, Callable
import numpy as np


class Proyectil:
    """
    Representa un proyectil físico y encapsula sus propiedades geométricas,
    de masa y aerodinámicas en un entorno gravitatorio y fluido (atmósfera).
    """

    def __init__(
        self,
        masa: float = 2.0,
        radio: float = 0.075,
        coeficiente_arrastre: float = 0.47,
        densidad_aire: float = 1.225,
        gravedad: float = 9.80665
    ) -> None:
        """
        Inicializa una instancia del Proyectil.

        Parámetros:
        -----------
        masa : float
            Masa del proyectil en kilogramos [kg] (m > 0).
        radio : float
            Radio de la sección esférica en metros [m] (r > 0).
        coeficiente_arrastre : float
            Coeficiente adimensional de arrastre Cd (ej. 0.47 para una esfera).
        densidad_aire : float
            Densidad del fluido (aire a nivel del mar) en [kg/m^3] (rho).
        gravedad : float
            Aceleración de la gravedad estándar [m/s^2].
        """
        if masa <= 0:
            raise ValueError("La masa del proyectil debe ser positiva.")
        if radio <= 0:
            raise ValueError("El radio del proyectil debe ser positivo.")

        self._masa = float(masa)
        self._radio = float(radio)
        self._cd = float(coeficiente_arrastre)
        self._rho = float(densidad_aire)
        self._g = float(gravedad)

    # --- Propiedades (Getters y Setters) ---
    @property
    def masa(self) -> float:
        """Masa del proyectil [kg]."""
        return self._masa

    @property
    def radio(self) -> float:
        """Radio del proyectil [m]."""
        return self._radio

    @property
    def gravedad(self) -> float:
        """Magnitud de la aceleración gravitatoria [m/s^2]."""
        return self._g

    @property
    def area_transversal(self) -> float:
        """Área de la sección transversal frontal A = pi * r^2 [m^2]."""
        return np.pi * (self._radio ** 2)

    @property
    def coeficiente_arrastre(self) -> float:
        """Coeficiente de arrastre Cd [adimensional]."""
        return self._cd

    @property
    def densidad_aire(self) -> float:
        """Densidad del fluido rho [kg/m^3]."""
        return self._rho

    @property
    def constante_arrastre_b(self) -> float:
        """
        Factor cuadrático de arrastre b = 0.5 * rho * Cd * A [kg/m].
        La fuerza de resistencia se modela como: F_d = -b * |v| * v_vec.
        """
        return 0.5 * self._rho * self._cd * self.area_transversal

    # --- Métodos de Dinámica y EDOs ---
    def calcular_aceleraciones(
        self,
        vx: float,
        vy: float,
        con_resistencia: bool = True,
        viento_x: float = 0.0
    ) -> Tuple[float, float]:
        """
        Calcula las componentes de la aceleración instantánea (ax, ay).

        Ecuaciones del movimiento:
        --------------------------
        Ideal:
            ax = 0
            ay = -g
        Con resistencia cuadrática y viento horizontal:
            v_rel_x = vx - viento_x
            v_rel_y = vy
            v_rel = sqrt(v_rel_x^2 + v_rel_y^2)
            Fdx = -b * v_rel * v_rel_x
            Fdy = -b * v_rel * v_rel_y
            ax = Fdx / m = -(b/m) * v_rel * (vx - viento_x)
            ay = -g + Fdy / m = -g - (b/m) * v_rel * vy

        Parámetros:
        -----------
        vx : float
            Componente de velocidad horizontal [m/s].
        vy : float
            Componente de velocidad vertical [m/s].
        con_resistencia : bool
            True para incluir fuerza de arrastre, False para caída libre ideal.
        viento_x : float
            Velocidad del viento horizontal en [m/s] (positivo a favor, negativo en contra).

        Retorna:
        --------
        Tuple[float, float]:
            (ax, ay) en [m/s^2].
        """
        if not con_resistencia:
            return 0.0, -self._g

        v_rel_x = vx - viento_x
        v_rel_y = vy
        v_rel_mag = np.hypot(v_rel_x, v_rel_y)
        factor_arrastre = self.constante_arrastre_b / self._masa
        
        ax = -factor_arrastre * v_rel_mag * v_rel_x
        ay = -self._g - (factor_arrastre * v_rel_mag * v_rel_y)
        return ax, ay

    def derivadas(
        self,
        t: float,
        estado: np.ndarray,
        con_resistencia: bool = True,
        viento_x: float = 0.0
    ) -> np.ndarray:
        """
        Vector de derivadas de primer orden dS/dt para el sistema dinámico.

        Estado S = [x, y, vx, vy]
        dS/dt    = [vx, vy, ax, ay]

        Parámetros:
        -----------
        t : float
            Tiempo actual [s].
        estado : np.ndarray
            Vector de estado [x, y, vx, vy].
        con_resistencia : bool
            Bandera para activar o desactivar el rozamiento aerodinámico.
        viento_x : float
            Velocidad del viento horizontal [m/s].

        Retorna:
        --------
        np.ndarray:
            Vector dS/dt = [vx, vy, ax, ay].
        """
        _, _, vx, vy = estado
        ax, ay = self.calcular_aceleraciones(vx, vy, con_resistencia=con_resistencia, viento_x=viento_x)
        return np.array([vx, vy, ax, ay], dtype=float)

    # --- Integradores Numéricos ---
    def paso_euler(
        self,
        t: float,
        estado: np.ndarray,
        dt: float,
        con_resistencia: bool = True,
        viento_x: float = 0.0
    ) -> np.ndarray:
        """
        Avanza el estado del proyectil un paso dt mediante el Método de Euler hacia adelante:
        S(t + dt) = S(t) + dt * f(t, S(t))
        """
        dS = self.derivadas(t, estado, con_resistencia=con_resistencia, viento_x=viento_x)
        return estado + dt * dS

    def paso_rk4(
        self,
        t: float,
        estado: np.ndarray,
        dt: float,
        con_resistencia: bool = True,
        viento_x: float = 0.0
    ) -> np.ndarray:
        """
        Avanza el estado del proyectil un paso dt mediante el Método de Runge-Kutta de 4to Orden (RK4).
        Proporciona un error de truncamiento local de O(dt^5) y global de O(dt^4).
        """
        k1 = self.derivadas(t, estado, con_resistencia=con_resistencia, viento_x=viento_x)
        k2 = self.derivadas(t + 0.5 * dt, estado + 0.5 * dt * k1, con_resistencia=con_resistencia, viento_x=viento_x)
        k3 = self.derivadas(t + 0.5 * dt, estado + 0.5 * dt * k2, con_resistencia=con_resistencia, viento_x=viento_x)
        k4 = self.derivadas(t + dt, estado + dt * k3, con_resistencia=con_resistencia, viento_x=viento_x)

        return estado + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)

    # --- Solución Analítica Exacta (Caso Ideal sin Resistencia) ---
    def solucion_analitica_ideal(
        self,
        t: np.ndarray,
        x0: float,
        y0: float,
        v0: float,
        theta_rad: float
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Calcula la cinemática analítica exacta para el tiro parabólico sin rozamiento.

        Retorna:
        --------
        (x, y, vx, vy, ax, ay) evaluados en cada instante de tiempo t.
        """
        vx0 = v0 * np.cos(theta_rad)
        vy0 = v0 * np.sin(theta_rad)

        x = x0 + vx0 * t
        y = y0 + vy0 * t - 0.5 * self._g * (t ** 2)
        vx = np.full_like(t, vx0)
        vy = vy0 - self._g * t
        ax = np.zeros_like(t)
        ay = np.full_like(t, -self._g)

        return x, y, vx, vy, ax, ay
