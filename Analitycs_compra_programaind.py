# --- Librerías ---
import pandas as pd
import numpy as np
 

# --- Cargar archivo (local) ---
ventas = pd.read_csv('ventas.csv', encoding='utf-8', sep=',')

# --- Selección y limpieza básica ---
ventaslimpio = ventas[["Correo electronico", "Fecha", "Producto"]].dropna()
ventaslimpio["Producto"] = ventaslimpio["Producto"].astype(str)
ventaslimpio["Fecha"] = pd.to_datetime(ventaslimpio["Fecha"], errors="coerce")

# --- Clasificación de productos ---
condiciones = [
    ventaslimpio["Producto"].str.contains("Free trial", case=False, na=False),
    ventaslimpio["Producto"].str.contains("Suscripcion FF", case=False, na=False),
    ventaslimpio["Producto"].str.contains("Trimestral", case=False, na=False),
    ventaslimpio["Producto"].str.contains("Semestral", case=False, na=False),
    ventaslimpio["Producto"].str.contains("Anual", case=False, na=False)
]

tipos = [
    "Free trial",
    "Suscripción FF",
    "Trimestral",
    "Semestral",
    "Anual"
]

ventaslimpio["Tipo"] = np.select(condiciones, tipos, default="Programa individual")

# --- Excluir becas ---
ventaslimpio = ventaslimpio[~ventaslimpio["Producto"].str.contains("beca", case=False, na=False)]

# --- Duraciones en meses ---
duracion_meses = {
    "Free trial": 1,
    "Suscripción FF": 1,
    "Trimestral": 3,
    "Semestral": 6,
    "Anual": 12,
    "Programa individual": 0
}

ventaslimpio["Duración (meses)"] = ventaslimpio["Tipo"].map(duracion_meses)

# --- Fecha de expiración (suma meses reales) ---
ventaslimpio["Fecha de expiración"] = ventaslimpio.apply(
    lambda x: x["Fecha"] + pd.DateOffset(months=x["Duración (meses)"]),
    axis=1
)

# --- Inicialización de columnas analíticas ---
ventaslimpio = ventaslimpio.sort_values(by=["Correo electronico", "Fecha"]).reset_index(drop=True)
ventaslimpio["Dias_activo_total"] = 0
ventaslimpio["Dias_hasta_recompra"] = np.nan
ventaslimpio["Dias_desde_alta_a_prog_individual"] = np.nan

# --- Análisis por usuario (cálculo de actividad, recompra, programa individual) ---
def analizar_usuario(grupo):
    grupo = grupo.sort_values("Fecha").reset_index(drop=True)

    total_dias = 0
    fecha_fin_anterior = None
    dias_hasta_recompra = []
    fecha_primer_alta = None
    fecha_prog_individual = None

    for i, fila in grupo.iterrows():
        tipo = fila["Tipo"]
        inicio = fila["Fecha"]
        vencimiento = fila["Fecha de expiración"]

        # Guardar primera fecha de alta
        if fecha_primer_alta is None:
            fecha_primer_alta = inicio

        # Si es suscripción (no programa individual)
        if tipo != "Programa individual":
            total_dias += (vencimiento - inicio).days
            fecha_fin_anterior = vencimiento
            dias_hasta_recompra.append(np.nan)
        else:
            # Programa individual
            if fecha_prog_individual is None:
                fecha_prog_individual = inicio
            if fecha_fin_anterior:
                diff = (inicio - fecha_fin_anterior).days
                dias_hasta_recompra.append(diff if diff >= 0 else 0)
            else:
                dias_hasta_recompra.append(np.nan)

    if len(dias_hasta_recompra) < len(grupo):
        dias_hasta_recompra += [np.nan] * (len(grupo) - len(dias_hasta_recompra))

    dias_a_prog = None
    if fecha_prog_individual and fecha_primer_alta:
        dias_a_prog = (fecha_prog_individual - fecha_primer_alta).days

    grupo["Dias_activo_total"] = total_dias
    grupo["Dias_hasta_recompra"] = dias_hasta_recompra
    grupo["Dias_desde_alta_a_prog_individual"] = dias_a_prog

    return grupo

# --- Aplicar el análisis ---
ventas_final = ventaslimpio.groupby("Correo electronico", group_keys=False).apply(analizar_usuario)

# --- Crear DataFrame resumen por usuario ---
def resumen_usuario(grupo):
    grupo = grupo.sort_values("Fecha").reset_index(drop=True)

    correo = grupo["Correo electronico"].iloc[0]
    fecha_primer_alta = grupo["Fecha"].min()
    fecha_ultima = max(grupo["Fecha"].max(), grupo["Fecha de expiración"].max())
    dias_activos = grupo["Dias_activo_total"].max()
    compro_prog = (grupo["Tipo"] == "Programa individual").any()
    dias_al_prog = grupo["Dias_desde_alta_a_prog_individual"].dropna().min() if compro_prog else np.nan
    dias_recompra = grupo["Dias_hasta_recompra"].dropna().iloc[-1] if grupo["Dias_hasta_recompra"].notna().any() else np.nan
    volvio = not pd.isna(dias_recompra)

    return pd.Series({
        "Correo electronico": correo,
        "Primera_fecha_alta": fecha_primer_alta,
        "Ultima_fecha_actividad": fecha_ultima,
        "Dias_activo_total": dias_activos,
        "Compro_programa_individual": compro_prog,
        "Dias_desde_alta_a_prog_individual": dias_al_prog,
        "Dias_hasta_recompra": dias_recompra,
        "Volvio_despues": volvio
    })

usuarios_df = ventas_final.groupby("Correo electronico").apply(resumen_usuario).reset_index(drop=True)

# --- Mostrar resultado ---
print("\nResumen por usuario:\n")
print(usuarios_df.head(15))

usuarios_df.to_excel("resumen_usuarios.xlsx", index=False)

# Lenny Thomas Portillo



