"""
===============================================================================
Trabajo Final Integrador (TFI) - Física I
Opción A: Simulación de Tiro Parabólico con y sin Resistencia del Aire
Carrera: Ingeniería en Informática
Módulo Principal: main.py
===============================================================================
Punto de entrada de la aplicación. Configura las variables del problema,
ejecuta las simulaciones numéricas y analíticas, imprime el informe tabulado
en consola y despliega las ventanas de análisis gráfico y animación dinámica.
"""

import sys
from modelo import Proyectil
from simulador import SimuladorTiro
from grafica import GraficadorTrayectoria
from animacion import AnimadorProyectil


def imprimir_encabezado():
    """Imprime el banner académico del proyecto."""
    print("=" * 80)
    print(" " * 15 + "TRABAJO FINAL INTEGRADOR - FÍSICA I")
    print(" " * 10 + "Opción A: Simulación del Tiro Parabólico con Resistencia del Aire")
    print(" " * 18 + "Facultad de Ingeniería en Informática")
    print("=" * 80)


def imprimir_parametros(proyectil: Proyectil, simulador: SimuladorTiro):
    """Muestra en consola las condiciones iniciales y coeficientes físicos."""
    print("\n" + "─" * 35 + " PARÁMETROS DEL SISTEMA " + "─" * 35)
    print(f" • Masa del Proyectil (m)         : {proyectil.masa:.3f} kg")
    print(f" • Radio del Proyectil (r)        : {proyectil.radio:.4f} m  (Área A = {proyectil.area_transversal:.5f} m²)")
    print(f" • Coeficiente de Arrastre (Cd)   : {proyectil.coeficiente_arrastre:.2f} (Esfera)")
    print(f" • Densidad del Aire (rho)        : {proyectil.densidad_aire:.3f} kg/m³")
    print(f" • Factor de Resistencia b = ½ρCdA: {proyectil.constante_arrastre_b:.6f} kg/m")
    print(f" • Aceleración Gravedad (g)       : {proyectil.gravedad:.5f} m/s²")
    print(f" • Rapidez Inicial (v0)           : {simulador.v0:.2f} m/s ({simulador.v0 * 3.6:.1f} km/h)")
    print(f" • Ángulo de Disparo (theta)      : {simulador.angulo_grados:.2f}°")
    print(f" • Posición Inicial (x0, y0)      : ({simulador.x0:.1f} m, {simulador.y0:.1f} m)")
    print("─" * 94)


def imprimir_tabla_comparativa(resultados: dict):
    """Genera una tabla comparativa con formato profesional en consola."""
    res_ideal = resultados["ideal_analitico"]
    res_rk4_ideal = resultados["ideal_rk4"]
    res_real = resultados["real_rk4"]
    res_euler = resultados["real_euler"]

    # Diferencias porcentuales respecto al caso ideal
    dif_alcance = ((res_real.alcance_maximo - res_ideal.alcance_maximo) / res_ideal.alcance_maximo) * 100
    dif_altura = ((res_real.altura_maxima - res_ideal.altura_maxima) / res_ideal.altura_maxima) * 100
    dif_tiempo = ((res_real.tiempo_vuelo - res_ideal.tiempo_vuelo) / res_ideal.tiempo_vuelo) * 100
    dif_v_impacto = ((res_real.velocidad_impacto - res_ideal.velocidad_impacto) / res_ideal.velocidad_impacto) * 100

    print("\n" + "═" * 94)
    print(f"{'TABLA COMPARATIVA DE RESULTADOS CINEMÁTICOS':^94}")
    print("═" * 94)
    print(f"{'Métrica':<28} | {'Ideal (Analítico)':^18} | {'Real (Arrastre RK4)':^20} | {'Variación / Impacto':^20}")
    print("─" * 94)
    print(f"{'Alcance Máximo (X_max)':<28} | {res_ideal.alcance_maximo:15.2f} m | {res_real.alcance_maximo:17.2f} m | {dif_alcance:17.2f} %")
    print(f"{'Altura Máxima (Y_max)':<28} | {res_ideal.altura_maxima:15.2f} m | {res_real.altura_maxima:17.2f} m | {dif_altura:17.2f} %")
    print(f"{'Posición X en Altura Máx':<28} | {res_ideal.pos_x_altura_maxima:15.2f} m | {res_real.pos_x_altura_maxima:17.2f} m | {'-':^20}")
    print(f"{'Tiempo de Vuelo Total':<28} | {res_ideal.tiempo_vuelo:15.2f} s | {res_real.tiempo_vuelo:17.2f} s | {dif_tiempo:17.2f} %")
    print(f"{'Tiempo a Altura Máxima':<28} | {res_ideal.tiempo_altura_maxima:15.2f} s | {res_real.tiempo_altura_maxima:17.2f} s | {'-':^20}")
    print(f"{'Velocidad de Impacto |v|':<28} | {res_ideal.velocidad_impacto:15.2f} m/s| {res_real.velocidad_impacto:17.2f} m/s| {dif_v_impacto:17.2f} %")
    print(f"{'Ángulo de Impacto':<28} | {res_ideal.angulo_impacto_deg:15.2f} ° | {res_real.angulo_impacto_deg:17.2f} ° | {'-':^20}")
    print("═" * 94)

    # Verificación de precisión numérica RK4 vs Solución Analítica
    err_alcance = abs(res_rk4_ideal.alcance_maximo - res_ideal.alcance_maximo)
    err_altura = abs(res_rk4_ideal.altura_maxima - res_ideal.altura_maxima)
    print("\n" + "─" * 30 + " VALIDACIÓN DEL MÉTODO NUMÉRICO (RK4) " + "─" * 30)
    print(f" • Error absoluto en Alcance (Ideal RK4 vs Analítico): {err_alcance:.2e} m")
    print(f" • Error absoluto en Altura  (Ideal RK4 vs Analítico): {err_altura:.2e} m")
    print(f" • Diferencia entre Euler y RK4 en caso real         : {abs(res_euler.alcance_maximo - res_real.alcance_maximo):.4f} m")
    print("─" * 94 + "\n")


def main():
    """Función principal de ejecución del proyecto."""
    imprimir_encabezado()

    # 1. Definición de Parámetros Físicos del Modelo
    # Ejemplo: Bala de cañón esférica o proyectil de prueba
    proyectil = Proyectil(
        masa=2.5,                  # 2.5 kg
        radio=0.075,               # 7.5 cm de radio (15 cm diámetro)
        coeficiente_arrastre=0.47, # Coeficiente de arrastre estándar de una esfera
        densidad_aire=1.225,       # Aire a 15°C al nivel del mar (kg/m³)
        gravedad=9.80665           # Gravedad estándar (m/s²)
    )

    # 2. Condiciones Iniciales de Lanzamiento
    simulador = SimuladorTiro(
        proyectil=proyectil,
        v0=70.0,                   # Velocidad inicial en m/s (252 km/h)
        angulo_grados=45.0,        # Ángulo óptimo en vacío
        x0=0.0,                    # Coordenada x inicial
        y0=0.0                     # Coordenada y inicial (a nivel del suelo)
    )

    imprimir_parametros(proyectil, simulador)

    # 3. Procesamiento y Ejecución de Simulaciones
    print("Calculando simulaciones cinemáticas y dinámicas con paso temporal dt=0.001 s...")
    resultados = simulador.ejecutar_estudio_completo(dt=0.001)

    # 4. Despliegue de Resultados Tabulados en Consola
    imprimir_tabla_comparativa(resultados)

    # 5. Visualización Estática (Matplotlib)
    print("Generando gráficos estáticos de trayectorias y cinemática...")
    graficador = GraficadorTrayectoria()
    graficador.graficar_trayectoria_2d(resultados, guardar_ruta="trayectoria_comparativa.png")
    graficador.graficar_cinematica_completa(resultados, guardar_ruta="cinematica_completa.png")
    print("Gráficos exportados con éxito como 'trayectoria_comparativa.png' y 'cinematica_completa.png'.")

    # 6. Animación Dinámica 2D en Tiempo Real
    print("\nIniciando visualización dinámica interactiva en 2D (Cierre la ventana para finalizar)...")
    animador = AnimadorProyectil(resultados, fps=60, factor_velocidad=1.0)
    animador.iniciar()


if __name__ == "__main__":
    main()
