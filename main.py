"""
===============================================================================
Trabajo Final Integrador (TFI) - Física I
Opción A: Simulación de Tiro Parabólico con y sin Resistencia del Aire
Carrera: Ingeniería en Informática
Módulo Principal: main.py
===============================================================================
Punto de entrada de la aplicación. Configura las variables del problema,
proporciona un menú interactivo en consola para modificar parámetros físicos,
de lanzamiento y de entorno (viento), ejecuta las simulaciones numéricas
y analíticas, imprime el informe tabulado y despliega las ventanas gráficas.
"""

import sys
from modelo import Proyectil
from simulador import SimuladorTiro
from grafica import GraficadorTrayectoria
from animacion import AnimadorProyectil
import menu


def imprimir_encabezado():
    """Imprime el banner académico del proyecto."""
    print("=" * 80)
    print(" " * 15 + "TRABAJO FINAL INTEGRADOR - FÍSICA I")
    print(" " * 10 + "Opción A: Simulación del Tiro Parabólico con Resistencia del Aire")
    print(" " * 18 + "Facultad de Ingeniería en Informática")
    print("=" * 80)


def imprimir_parametros(proyectil: Proyectil, simulador: SimuladorTiro):
    """Muestra en consola las condiciones iniciales y coeficientes físicos."""
    viento_desc = (
        f"{simulador.viento_x:+.2f} m/s (A favor +x)" if simulador.viento_x > 0
        else f"{simulador.viento_x:+.2f} m/s (En contra -x)" if simulador.viento_x < 0
        else "0.00 m/s (Sin viento)"
    )

    print("\n" + "─" * 35 + " PARÁMETROS DEL SISTEMA " + "─" * 35)
    print(f" • Masa del Proyectil (m)         : {proyectil.masa:.3f} kg")
    print(f" • Radio del Proyectil (r)        : {proyectil.radio:.4f} m  (Área A = {proyectil.area_transversal:.5f} m²)")
    print(f" • Coeficiente de Arrastre (Cd)   : {proyectil.coeficiente_arrastre:.2f}")
    print(f" • Densidad del Fluido (rho)      : {proyectil.densidad_aire:.3f} kg/m³")
    print(f" • Factor de Resistencia b = ½ρCdA: {proyectil.constante_arrastre_b:.6f} kg/m")
    print(f" • Aceleración Gravedad (g)       : {proyectil.gravedad:.5f} m/s²")
    print(f" • Velocidad del Viento (vw)      : {viento_desc}")
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
    if res_ideal.alcance_maximo != 0:
        dif_alcance = ((res_real.alcance_maximo - res_ideal.alcance_maximo) / res_ideal.alcance_maximo) * 100
        dif_alcance_str = f"{dif_alcance:17.2f} %"
    else:
        dif_alcance_str = f"{'-':^20}"

    if res_ideal.altura_maxima != 0:
        dif_altura = ((res_real.altura_maxima - res_ideal.altura_maxima) / res_ideal.altura_maxima) * 100
        dif_altura_str = f"{dif_altura:17.2f} %"
    else:
        dif_altura_str = f"{'-':^20}"

    if res_ideal.tiempo_vuelo != 0:
        dif_tiempo = ((res_real.tiempo_vuelo - res_ideal.tiempo_vuelo) / res_ideal.tiempo_vuelo) * 100
        dif_tiempo_str = f"{dif_tiempo:17.2f} %"
    else:
        dif_tiempo_str = f"{'-':^20}"

    if res_ideal.velocidad_impacto != 0:
        dif_v_impacto = ((res_real.velocidad_impacto - res_ideal.velocidad_impacto) / res_ideal.velocidad_impacto) * 100
        dif_v_impacto_str = f"{dif_v_impacto:17.2f} %"
    else:
        dif_v_impacto_str = f"{'-':^20}"

    print("\n" + "═" * 94)
    print(f"{'TABLA COMPARATIVA DE RESULTADOS CINEMÁTICOS':^94}")
    print("═" * 94)
    print(f"{'Métrica':<28} | {'Ideal (Analítico)':^18} | {'Real (Arrastre RK4)':^20} | {'Variación / Impacto':^20}")
    print("─" * 94)
    print(f"{'Alcance Máximo (X_max)':<28} | {res_ideal.alcance_maximo:15.2f} m | {res_real.alcance_maximo:17.2f} m | {dif_alcance_str}")
    print(f"{'Altura Máxima (Y_max)':<28} | {res_ideal.altura_maxima:15.2f} m | {res_real.altura_maxima:17.2f} m | {dif_altura_str}")
    print(f"{'Posición X en Altura Máx':<28} | {res_ideal.pos_x_altura_maxima:15.2f} m | {res_real.pos_x_altura_maxima:17.2f} m | {'-':^20}")
    print(f"{'Tiempo de Vuelo Total':<28} | {res_ideal.tiempo_vuelo:15.2f} s | {res_real.tiempo_vuelo:17.2f} s | {dif_tiempo_str}")
    print(f"{'Tiempo a Altura Máxima':<28} | {res_ideal.tiempo_altura_maxima:15.2f} s | {res_real.tiempo_altura_maxima:17.2f} s | {'-':^20}")
    print(f"{'Velocidad de Impacto |v|':<28} | {res_ideal.velocidad_impacto:15.2f} m/s| {res_real.velocidad_impacto:17.2f} m/s| {dif_v_impacto_str}")
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


def ejecutar_simulacion_actual(
    masa: float,
    radio: float,
    cd: float,
    densidad_aire: float,
    gravedad: float,
    v0: float,
    angulo: float,
    x0: float,
    y0: float,
    viento_x: float,
    opciones_vis: dict
):
    """Ejecuta el cálculo físico y despliega los resultados gráficos según la configuración."""
    try:
        proyectil = Proyectil(
            masa=masa,
            radio=radio,
            coeficiente_arrastre=cd,
            densidad_aire=densidad_aire,
            gravedad=gravedad
        )

        simulador = SimuladorTiro(
            proyectil=proyectil,
            v0=v0,
            angulo_grados=angulo,
            x0=x0,
            y0=y0,
            viento_x=viento_x
        )
    except Exception as e:
        print(f"\n❌ Error al instanciar el modelo físico: {e}")
        return

    # 1. Resumen de parámetros
    imprimir_parametros(proyectil, simulador)

    # 2. Ejecución numérica y analítica
    dt = opciones_vis.get("dt", 0.001)
    print(f"Calculando simulaciones cinemáticas y dinámicas con paso temporal dt = {dt} s...")
    resultados = simulador.ejecutar_estudio_completo(dt=dt)

    # 3. Reporte tabular en consola
    imprimir_tabla_comparativa(resultados)

    # 4. Gráficos Estáticos
    if opciones_vis["mostrar_grafico_trayectoria"] or opciones_vis["mostrar_grafico_cinematica"]:
        print("Generando gráficos estáticos de trayectorias y cinemática...")
        graficador = GraficadorTrayectoria()
        if opciones_vis["mostrar_grafico_trayectoria"]:
            graficador.graficar_trayectoria_2d(resultados, guardar_ruta="trayectoria_comparativa.png")
        if opciones_vis["mostrar_grafico_cinematica"]:
            graficador.graficar_cinematica_completa(resultados, guardar_ruta="cinematica_completa.png")
        print("Gráficos listos (Cierre las ventanas gráficas para continuar)...")
        graficador.mostrar()

    # 5. Animación Dinámica
    if opciones_vis["mostrar_animacion"]:
        print("\nIniciando visualización dinámica interactiva en 2D (Cierre la ventana para volver al menú)...")
        animador = AnimadorProyectil(
            resultados,
            fps=60,
            factor_velocidad=opciones_vis["factor_velocidad"]
        )
        animador.iniciar()


def main():
    """Función principal y bucle interactivo de ejecución."""
    imprimir_encabezado()

    # Variables de estado iniciales (Valores por defecto)
    masa = 2.5
    radio = 0.075
    cd = 0.47
    densidad_aire = 1.225
    gravedad = 9.80665

    v0 = 70.0
    angulo = 45.0
    x0 = 0.0
    y0 = 0.0
    viento_x = 0.0

    opciones_vis = {
        "mostrar_grafico_trayectoria": True,
        "mostrar_grafico_cinematica": True,
        "mostrar_animacion": True,
        "factor_velocidad": 1.0,
        "dt": 0.001
    }

    # Bucle interactivo principal
    while True:
        try:
            opcion = menu.mostrar_menu_principal()

            if opcion == "1":
                ejecutar_simulacion_actual(
                    masa, radio, cd, densidad_aire, gravedad,
                    v0, angulo, x0, y0, viento_x, opciones_vis
                )

            elif opcion == "2":
                v0, angulo, x0, y0 = menu.menu_modificar_lanzamiento(v0, angulo, x0, y0)

            elif opcion == "3":
                masa, radio, cd = menu.menu_modificar_proyectil(masa, radio, cd)

            elif opcion == "4":
                densidad_aire, gravedad, viento_x = menu.menu_modificar_entorno(densidad_aire, gravedad, viento_x)

            elif opcion == "5":
                print("\n  [1] Cargar Preset de Proyectil")
                print("  [2] Cargar Preset de Entorno Planetario")
                print("  [0] Volver")
                sub_opc = input("  👉 Seleccione: ").strip()
                if sub_opc == "1":
                    res_proy = menu.menu_presets_proyectiles()
                    if res_proy is not None:
                        masa, radio, cd = res_proy
                elif sub_opc == "2":
                    res_ent = menu.menu_presets_entornos()
                    if res_ent is not None:
                        densidad_aire, gravedad = res_ent

            elif opcion == "6":
                proy_temp = Proyectil(masa=masa, radio=radio, coeficiente_arrastre=cd, densidad_aire=densidad_aire, gravedad=gravedad)
                sim_temp = SimuladorTiro(proyectil=proy_temp, v0=v0, angulo_grados=angulo, x0=x0, y0=y0, viento_x=viento_x)
                imprimir_parametros(proy_temp, sim_temp)

            elif opcion == "7":
                opciones_vis = menu.menu_opciones_visualizacion(opciones_vis)

            elif opcion == "0":
                print("\n  👋 Finalizando el programa. ¡Éxitos en la defensa del TFI!")
                break

            else:
                print("  ⚠️ Opción no reconocida. Por favor, ingrese un número del 0 al 7.")

        except KeyboardInterrupt:
            print("\n\n  👋 Ejecución interrumpida por el usuario. Saliendo...")
            break
        except Exception as e:
            print(f"\n  ❌ Ocurrió un error inesperado: {e}")


if __name__ == "__main__":
    main()

