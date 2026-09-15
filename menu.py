"""
===============================================================================
Trabajo Final Integrador (TFI) - Física I
Opción A: Simulación de Tiro Parabólico con y sin Resistencia del Aire
Módulo: menu.py
===============================================================================
Proporciona un menú interactivo en consola, robusto y profesional, diseñado
para la defensa del examen final. Permite modificar dinámicamente cualquier
variable física, cinemática y de entorno (incluyendo viento), cargar presets
y controlar las opciones de visualización sin reiniciar el programa.
"""

from typing import Tuple, Dict, Any
from modelo import Proyectil
from simulador import SimuladorTiro


# Presets predefinidos de proyectiles reales
PRESETS_PROYECTILES = {
    "1": {
        "nombre": "Bala de Cañón Esférica (Por defecto)",
        "masa": 2.5,
        "radio": 0.075,
        "cd": 0.47,
        "descripcion": "Hierro fundido, 15 cm de diámetro, arrastre de esfera."
    },
    "2": {
        "nombre": "Pelota de Béisbol",
        "masa": 0.145,
        "radio": 0.037,
        "cd": 0.30,
        "descripcion": "Masa estándar 145g, radio 3.7cm."
    },
    "3": {
        "nombre": "Pelota de Fútbol",
        "masa": 0.430,
        "radio": 0.110,
        "cd": 0.25,
        "descripcion": "Reglamentaria FIFA #5, 430g, radio 11cm."
    },
    "4": {
        "nombre": "Pelota de Tenis",
        "masa": 0.058,
        "radio": 0.033,
        "cd": 0.55,
        "descripcion": "Superficie de fieltro rugosa (mayor arrastre)."
    },
    "5": {
        "nombre": "Bala de Fusil / Proyectil Ojival",
        "masa": 0.010,
        "radio": 0.0045,
        "cd": 0.15,
        "descripcion": "Forma altamente aerodinámica, bajo coeficiente de arrastre."
    }
}

# Presets de entornos planetarios y atmosféricos
PRESETS_ENTORNOS = {
    "1": {
        "nombre": "Tierra - Nivel del Mar (15°C)",
        "gravedad": 9.80665,
        "densidad_aire": 1.225,
        "descripcion": "Condiciones estándar ISA a nivel del mar."
    },
    "2": {
        "nombre": "Tierra - Gran Altitud (La Paz, 3600m)",
        "gravedad": 9.79000,
        "densidad_aire": 0.850,
        "descripcion": "Menor densidad de aire -> menor resistencia aerodinámica."
    },
    "3": {
        "nombre": "Luna (Vacío)",
        "gravedad": 1.62000,
        "densidad_aire": 0.000,
        "descripcion": "Sin atmósfera (arrastre nulo), gravedad 1/6 de la Tierra."
    },
    "4": {
        "nombre": "Marte",
        "gravedad": 3.71000,
        "densidad_aire": 0.020,
        "descripcion": "Atmósfera muy tenue de CO2 y gravedad reducida."
    },
    "5": {
        "nombre": "Júpiter",
        "gravedad": 24.7900,
        "densidad_aire": 1.330,
        "descripcion": "Gravedad superficial extrema."
    }
}


def leer_flotante(
    mensaje: str,
    valor_actual: float,
    min_val: float = None,
    max_val: float = None,
    permitir_cero: bool = True
) -> float:
    """
    Solicita un valor float por consola con validación robusta y valor por defecto al pulsar Enter.
    """
    while True:
        prompt = f"  👉 {mensaje} [Actual: {valor_actual}]: "
        entrada = input(prompt).strip()
        if not entrada:
            return float(valor_actual)
        try:
            val = float(entrada.replace(",", "."))
            if min_val is not None:
                if permitir_cero and val < min_val:
                    print(f"    ⚠️ Error: El valor debe ser mayor o igual a {min_val}.")
                    continue
                elif not permitir_cero and val <= min_val:
                    print(f"    ⚠️ Error: El valor debe ser estrictamente mayor a {min_val}.")
                    continue
            if max_val is not None and val > max_val:
                print(f"    ⚠️ Error: El valor no puede superar {max_val}.")
                continue
            return val
        except ValueError:
            print("    ⚠️ Error: Entrada inválida. Ingrese un número válido (ej. 15.5).")


def menu_modificar_lanzamiento(v0: float, angulo: float, x0: float, y0: float) -> Tuple[float, float, float, float]:
    """Menú para modificar condiciones iniciales de disparo."""
    print("\n" + "┌" + "─" * 60 + "┐")
    print("│         MODIFICAR PARÁMETROS DE LANZAMIENTO                │")
    print("├" + "─" * 60 + "┤")
    print("│  (Presione [ENTER] en cualquier campo para mantener actual) │")
    print("└" + "─" * 60 + "┘")

    nuevo_v0 = leer_flotante("Rapidez inicial v0 [m/s]", v0, min_val=0.0, permitir_cero=False)
    nuevo_ang = leer_flotante("Ángulo de tiro theta [°] (0° a 90°)", angulo, min_val=0.0, max_val=90.0)
    nuevo_x0 = leer_flotante("Posición horizontal inicial x0 [m]", x0)
    nuevo_y0 = leer_flotante("Altura vertical inicial y0 [m]", y0, min_val=0.0)

    print("\n  ✅ Parámetros de lanzamiento actualizados con éxito.")
    return nuevo_v0, nuevo_ang, nuevo_x0, nuevo_y0


def menu_modificar_proyectil(masa: float, radio: float, cd: float) -> Tuple[float, float, float]:
    """Menú para modificar propiedades físicas y geométricas del proyectil."""
    print("\n" + "┌" + "─" * 60 + "┐")
    print("│         MODIFICAR PROPIEDADES DEL PROYECTIL                │")
    print("├" + "─" * 60 + "┤")
    print("│  (Presione [ENTER] en cualquier campo para mantener actual) │")
    print("└" + "─" * 60 + "┘")

    nueva_m = leer_flotante("Masa del proyectil m [kg]", masa, min_val=0.0, permitir_cero=False)
    nuevo_r = leer_flotante("Radio del proyectil r [m]", radio, min_val=0.0, permitir_cero=False)
    nuevo_cd = leer_flotante("Coeficiente de arrastre Cd [adimensional]", cd, min_val=0.0)

    print("\n  ✅ Propiedades del proyectil actualizadas con éxito.")
    return nueva_m, nuevo_r, nuevo_cd


def menu_modificar_entorno(rho: float, g: float, viento_x: float) -> Tuple[float, float, float]:
    """Menú para modificar el entorno atmosférico, gravitatorio y viento."""
    print("\n" + "┌" + "─" * 60 + "┐")
    print("│         MODIFICAR ENTORNO FÍSICO Y VIENTO                  │")
    print("├" + "─" * 60 + "┤")
    print("│  (Presione [ENTER] en cualquier campo para mantener actual) │")
    print("└" + "─" * 60 + "┘")

    nuevo_rho = leer_flotante("Densidad del fluido rho [kg/m³]", rho, min_val=0.0)
    nuevo_g = leer_flotante("Aceleración de gravedad g [m/s²]", g, min_val=0.0, permitir_cero=False)
    nuevo_viento = leer_flotante("Velocidad de viento horizontal [m/s] (+ a favor, - en contra)", viento_x)

    print("\n  ✅ Parámetros de entorno y viento actualizados con éxito.")
    return nuevo_rho, nuevo_g, nuevo_viento


def menu_presets_proyectiles() -> Tuple[float, float, float]:
    """Permite seleccionar un proyectil preconfigurado."""
    print("\n" + "┌" + "─" * 65 + "┐")
    print("│                 SELECCIÓN DE PRESET DE PROYECTIL                │")
    print("├" + "─" * 65 + "┤")
    for k, p in PRESETS_PROYECTILES.items():
        print(f"│  [{k}] {p['nombre']:<32} (m={p['masa']}kg, r={p['radio']}m, Cd={p['cd']}) │")
    print("│  [0] Cancelar / Volver                                          │")
    print("└" + "─" * 65 + "┘")

    while True:
        opc = input("  👉 Seleccione un preset [0-5]: ").strip()
        if opc == "0":
            return None
        if opc in PRESETS_PROYECTILES:
            seleccion = PRESETS_PROYECTILES[opc]
            print(f"\n  🎯 Cargado preset: {seleccion['nombre']} ({seleccion['descripcion']})")
            return seleccion["masa"], seleccion["radio"], seleccion["cd"]
        print("  ⚠️ Opción inválida.")


def menu_presets_entornos() -> Tuple[float, float]:
    """Permite seleccionar un entorno planetario/atmosférico preconfigurado."""
    print("\n" + "┌" + "─" * 65 + "┐")
    print("│                 SELECCIÓN DE ENTORNO PLANETARIO                 │")
    print("├" + "─" * 65 + "┤")
    for k, e in PRESETS_ENTORNOS.items():
        print(f"│  [{k}] {e['nombre']:<35} (g={e['gravedad']} m/s², rho={e['densidad_aire']}) │")
    print("│  [0] Cancelar / Volver                                          │")
    print("└" + "─" * 65 + "┘")

    while True:
        opc = input("  👉 Seleccione un entorno [0-5]: ").strip()
        if opc == "0":
            return None
        if opc in PRESETS_ENTORNOS:
            seleccion = PRESETS_ENTORNOS[opc]
            print(f"\n  🪐 Cargado entorno: {seleccion['nombre']} ({seleccion['descripcion']})")
            return seleccion["densidad_aire"], seleccion["gravedad"]
        print("  ⚠️ Opción inválida.")


def menu_opciones_visualizacion(opciones: Dict[str, Any]) -> Dict[str, Any]:
    """Configuración de despliegue visual (gráficos estáticos y animación)."""
    while True:
        print("\n" + "┌" + "─" * 58 + "┐")
        print("│            CONFIGURACIÓN DE VISUALIZACIÓN                │")
        print("├" + "─" * 58 + "┤")
        estado_graf_tray = "ACTIVADO" if opciones["mostrar_grafico_trayectoria"] else "DESACTIVADO"
        estado_anim = "ACTIVADO" if opciones["mostrar_animacion"] else "DESACTIVADO"
        print(f"│  [1] Gráfico de Trayectoria 2D       : [{estado_graf_tray:<12}] │")
        print(f"│  [2] Animación 2D en Tiempo Real     : [{estado_anim:<12}] │")
        print(f"│  [3] Velocidad de Animación          : [{opciones['factor_velocidad']:.1f}x{' ' * 9}] │")
        print(f"│  [4] Paso Temporal Simulación (dt)   : [{opciones['dt']:.4f} s{' ' * 7}] │")
        print("│  [0] Volver al Menú Principal                            │")
        print("└" + "─" * 58 + "┘")

        opc = input("  👉 Seleccione opción a alternar o modificar [0-4]: ").strip()
        if opc == "0":
            break
        elif opc == "1":
            opciones["mostrar_grafico_trayectoria"] = not opciones["mostrar_grafico_trayectoria"]
        elif opc == "2":
            opciones["mostrar_animacion"] = not opciones["mostrar_animacion"]
        elif opc == "3":
            nuevo_factor = leer_flotante("Factor de velocidad (1.0 = real, 0.5 = lenta)", opciones["factor_velocidad"], min_val=0.1, max_val=5.0)
            opciones["factor_velocidad"] = nuevo_factor
        elif opc == "4":
            nuevo_dt = leer_flotante("Paso de tiempo dt [s] (ej. 0.001)", opciones["dt"], min_val=0.00001, max_val=0.1, permitir_cero=False)
            opciones["dt"] = nuevo_dt

    return opciones


def mostrar_menu_principal() -> str:
    """Muestra el panel principal de opciones del simulador."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║                     MENÚ PRINCIPAL DE CONTROL                      ║")
    print("╠" + "═" * 68 + "╣")
    print("║  [1] 🚀 Ejecutar Simulación con Parámetros Actuales                ║")
    print("║  [2] 🎯 Modificar Condiciones de Lanzamiento (v0, theta, x0, y0)   ║")
    print("║  [3] ⚙️  Modificar Propiedades del Proyectil (m, r, Cd)             ║")
    print("║  [4] 🌍 Modificar Entorno Físico y Viento (rho, g, vw)             ║")
    print("║  [5] 📦 Cargar Presets (Proyectiles / Entornos Planetarios)        ║")
    print("║  [6] 📊 Ver Resumen de Parámetros Actuales del Sistema             ║")
    print("║  [7] 🖥️  Configurar Opciones de Visualización (Gráficos/Animación) ║")
    print("║  [0] 🚪 Salir del Programa                                         ║")
    print("╚" + "═" * 68 + "╝")
    return input("  👉 Ingrese su opción [0-7]: ").strip()
