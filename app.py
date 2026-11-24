import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Simulador Cable Preensamblado | 2x50+50 y 3x50+50",
    page_icon="⚡",
    layout="wide"
)

# 0. CATÁLOGO DE PRODUCTOS Y VALORES POR DEFECTO
PRODUCTOS = {
    "CABLE PREENSAMBLADO ASC - AAAC 2 X 50 + 1 X 50 MM2": {
        "nombre_corto": "2x50 + 1x50 mm²",
        "fases": 2,
        "neutros": 1,
        "receta": [
            {"Componente": "Fase ASC - Al 1350", "Actual (kg/km)": 135.97, "Compactado (kg/km)": 135.97},
            {"Componente": "Fase ASC - XLPE NEG", "Actual (kg/km)": 53.60, "Compactado (kg/km)": 41.00},
            {"Componente": "Neutro AAAC - Al 6201", "Actual (kg/km)": 134.17, "Compactado (kg/km)": 134.17},
            {"Componente": "Neutro AAAC - XLPE NEG", "Actual (kg/km)": 53.73, "Compactado (kg/km)": 53.73},
        ],
        "tiempos": [
            {"Proceso": "Trefilado", "Actual (hrs/km)": 0.90, "Compactado (hrs/km)": 0.90, "Detalle / Alcance": "Tiempo total trefilado conductores"},
            {"Proceso": "Cableado", "Actual (hrs/km)": 1.60, "Compactado (hrs/km)": 1.80, "Detalle / Alcance": "Tiempo total cableado normal vs. compactado"},
            {"Proceso": "Extrusado", "Actual (hrs/km)": 3.30, "Compactado (hrs/km)": 2.85, "Detalle / Alcance": "Tiempo total aislamiento XLPE (fases + neutro)"},
            {"Proceso": "Trenzado", "Actual (hrs/km)": 0.90, "Compactado (hrs/km)": 0.85, "Detalle / Alcance": "Tiempo total reunido / preensamblado final"},
        ]
    },
    "CABLE PREENSAMBLADO ASC - AAAC 3 X 50 + 1 X 50 MM2": {
        "nombre_corto": "3x50 + 1x50 mm²",
        "fases": 3,
        "neutros": 1,
        "receta": [
            {"Componente": "Fase ASC - Al 1350", "Actual (kg/km)": 135.97, "Compactado (kg/km)": 135.97},
            {"Componente": "Fase ASC - XLPE NEG", "Actual (kg/km)": 53.60, "Compactado (kg/km)": 41.00},
            {"Componente": "Neutro AAAC - Al 6201", "Actual (kg/km)": 134.17, "Compactado (kg/km)": 134.17},
            {"Componente": "Neutro AAAC - XLPE NEG", "Actual (kg/km)": 53.73, "Compactado (kg/km)": 53.73},
        ],
        "tiempos": [
            {"Proceso": "Trefilado", "Actual (hrs/km)": 1.35, "Compactado (hrs/km)": 1.35, "Detalle / Alcance": "Tiempo total trefilado conductores (3 fases)"},
            {"Proceso": "Cableado", "Actual (hrs/km)": 2.40, "Compactado (hrs/km)": 2.70, "Detalle / Alcance": "Tiempo total cableado normal vs. compactado (3 fases)"},
            {"Proceso": "Extrusado", "Actual (hrs/km)": 4.40, "Compactado (hrs/km)": 3.80, "Detalle / Alcance": "Tiempo total aislamiento XLPE (3 fases + 1 neutro)"},
            {"Proceso": "Trenzado", "Actual (hrs/km)": 1.05, "Compactado (hrs/km)": 1.00, "Detalle / Alcance": "Tiempo total reunido / preensamblado final"},
        ]
    }
}

# INICIALIZAR MEMORIA PERSISTENTE (SESSION STATE)
if "mem_recetas" not in st.session_state:
    st.session_state.mem_recetas = {
        prod: pd.DataFrame(datos["receta"]) for prod, datos in PRODUCTOS.items()
    }

if "mem_tiempos" not in st.session_state:
    st.session_state.mem_tiempos = {
        prod: pd.DataFrame(datos["tiempos"]) for prod, datos in PRODUCTOS.items()
    }

if "mem_cif" not in st.session_state:
    st.session_state.mem_cif = pd.DataFrame([
        {
            "Proceso": "Trefilado",
            "Costo Mano de Obra Directa": 12.00,
            "Costo Mano de Obra Indirecta": 5.00,
            "Costos Indirectos de Fabricación": 18.00
        },
        {
            "Proceso": "Cableado",
            "Costo Mano de Obra Directa": 14.00,
            "Costo Mano de Obra Indirecta": 6.00,
            "Costos Indirectos de Fabricación": 22.00
        },
        {
            "Proceso": "Extrusado",
            "Costo Mano de Obra Directa": 16.00,
            "Costo Mano de Obra Indirecta": 7.50,
            "Costos Indirectos de Fabricación": 28.00
        },
        {
            "Proceso": "Trenzado",
            "Costo Mano de Obra Directa": 15.00,
            "Costo Mano de Obra Indirecta": 6.50,
            "Costos Indirectos de Fabricación": 24.00
        }
    ])

if "mem_hist" not in st.session_state:
    st.session_state.mem_hist = pd.DataFrame([
        {"Año / Periodo": "2024", "Metros 2x50 + 50": 697098, "Metros 3x50 + 50": 83765},
        {"Año / Periodo": "2025", "Metros 2x50 + 50": 571272, "Metros 3x50 + 50": 62869},
        {"Año / Periodo": "2026 (YTD)", "Metros 2x50 + 50": 411499, "Metros 3x50 + 50": 59976},
    ])

# Callbacks para guardar cambios en vivo sin perderlos al cambiar de producto o pestaña
def guardar_receta(prod_key, editor_key):
    cambios = st.session_state[editor_key].get("edited_rows", {})
    df_actual = st.session_state.mem_recetas[prod_key]
    for idx_str, cols in cambios.items():
        idx = int(idx_str)
        for col, val in cols.items():
            df_actual.at[idx, col] = val

def guardar_tiempos(prod_key, editor_key):
    cambios = st.session_state[editor_key].get("edited_rows", {})
    df_actual = st.session_state.mem_tiempos[prod_key]
    for idx_str, cols in cambios.items():
        idx = int(idx_str)
        for col, val in cols.items():
            df_actual.at[idx, col] = val

def guardar_cif(editor_key):
    cambios = st.session_state[editor_key].get("edited_rows", {})
    df_actual = st.session_state.mem_cif
    for idx_str, cols in cambios.items():
        idx = int(idx_str)
        for col, val in cols.items():
            df_actual.at[idx, col] = val

def guardar_hist(editor_key):
    cambios = st.session_state[editor_key].get("edited_rows", {})
    df_actual = st.session_state.mem_hist
    for idx_str, cols in cambios.items():
        idx = int(idx_str)
        for col, val in cols.items():
            df_actual.at[idx, col] = val

# ENCABEZADO PRINCIPAL
st.title("⚡ Simulador de Producción: Cable Preensamblado")

# 1. PANEL LATERAL: SELECTOR DE PRODUCTO, VOLUMEN Y COSTOS BASE
st.sidebar.header("🔌 0. Selección de Producto")
producto_sel = st.sidebar.selectbox(
    "Modelo de Cable Preensamblado:",
    options=list(PRODUCTOS.keys()),
    index=0
)
info_prod = PRODUCTOS[producto_sel]
num_fases = info_prod["fases"]
num_neutros = info_prod["neutros"]

st.subheader(f"{producto_sel} | Actual vs. Compactado")
st.markdown("Los cambios que realices en **tiempos**, **recetas** y **costos indirectos** se guardan automáticamente al cambiar entre productos.")
st.divider()

st.sidebar.divider()
st.sidebar.header("📏 1. Orden de Producción")
metros = st.sidebar.number_input(
    "Cantidad a fabricar (Metros):",
    min_value=1,
    max_value=10000000,
    value=1000,
    step=100
)
km = metros / 1000.0
st.sidebar.caption(f"Equivalente a: **{km:,.3f} km**")

st.sidebar.divider()
st.sidebar.header("💲 2. Costos de Materia Prima ($/kg)")
costo_al_1350 = st.sidebar.number_input(
    "ALAMBRE DE ALUMINIO 1350 9.50 MM H14 ($/kg):",
    min_value=0.0,
    value=4.2700,
    step=0.01,
    format="%.4f"
)
costo_al_6201 = st.sidebar.number_input(
    "ALAMBRE DE ALUMINIO 6201 3.00 MM ($/kg):",
    min_value=0.0,
    value=5.2416,
    step=0.01,
    format="%.4f"
)
costo_xlpe = st.sidebar.number_input(
    "XLPE NEG ($/kg):",
    min_value=0.0,
    value=2.2865,
    step=0.01,
    format="%.4f"
)

# 2. CONFIGURACIÓN DE RECETAS DE MATERIA PRIMA (CON PERSISTENCIA)
with st.expander(f"📦 Ver / Editar Receta Unitaria por Conductor - {info_prod['nombre_corto']} (kg/km)", expanded=False):
    st.caption(f"Nota: Los consumos de Fase se multiplican por **{num_fases}** y el Neutro por **{num_neutros}**.")
    key_rec = f"ed_rec_{info_prod['nombre_corto']}"
    recetas_edit = st.data_editor(
        st.session_state.mem_recetas[producto_sel],
        key=key_rec,
        on_change=guardar_receta,
        args=(producto_sel, key_rec),
        hide_index=True,
        use_container_width=True,
        disabled=["Componente"]
    )

# 3. ESTRUCTURA DE PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs([
    "🏭 Tiempos y Costos Indirectos (Modificable)",
    "⏱️ Comparativa Tiempos y Costos Totales",
    "📋 Comparativa Materia Prima", 
    "📈 Gráficos Ejecutivos e Histórico (2024–2026)"
])

# PESTAÑA 1: CONFIGURACIÓN MODIFICABLE DE TIEMPOS Y COSTOS POR PROCESO
with tab1:
    st.markdown(f"### ⏱️ 1. Tiempos Totales por Proceso para **{info_prod['nombre_corto']}** (hrs/km)")
    st.markdown("Ingresa el **tiempo total (hrs/km)** de cada proceso. Tus cambios quedan guardados aunque cambies de calibre.")
    
    key_tiemp = f"ed_tiemp_{info_prod['nombre_corto']}"
    tiempos_edit = st.data_editor(
        st.session_state.mem_tiempos[producto_sel],
        key=key_tiemp,
        on_change=guardar_tiempos,
        args=(producto_sel, key_tiemp),
        use_container_width=True,
        hide_index=True,
        disabled=["Proceso"],
        column_config={
            "Proceso": st.column_config.TextColumn("Proceso"),
            "Actual (hrs/km)": st.column_config.NumberColumn("Tiempo Total Actual (hrs/km)", min_value=0.0, format="%.2f", required=True),
            "Compactado (hrs/km)": st.column_config.NumberColumn("Tiempo Total Compactado (hrs/km)", min_value=0.0, format="%.2f", required=True),
            "Detalle / Alcance": st.column_config.TextColumn("Observación")
        }
    )

    st.divider()
    st.markdown("### 🏭 2. Costos Indirectos y Mano de Obra por Proceso ($/Hora-Máquina)")
    st.markdown("Tarifas horarias compartidas de planta. La columna **Total ($/hr)** se calcula automáticamente y permanece guardada.")
    
    key_cif = "ed_cif_global"
    procesos_edit = st.data_editor(
        st.session_state.mem_cif,
        key=key_cif,
        on_change=guardar_cif,
        args=(key_cif,),
        use_container_width=True,
        hide_index=True,
        disabled=["Proceso"],
        column_config={
            "Proceso": st.column_config.TextColumn("Proceso / Línea"),
            "Costo Mano de Obra Directa": st.column_config.NumberColumn("Costo Mano de Obra Directa ($/hr)", min_value=0.0, format="$%.2f", required=True),
            "Costo Mano de Obra Indirecta": st.column_config.NumberColumn("Costo Mano de Obra Indirecta ($/hr)", min_value=0.0, format="$%.2f", required=True),
            "Costos Indirectos de Fabricación": st.column_config.NumberColumn("Costos Indirectos de Fabricación ($/hr)", min_value=0.0, format="$%.2f", required=True),
        }
    )
    
    # Calcular columna Total ($/hr)
    df_proc_calc = st.session_state.mem_cif.copy()
    for col in ["Costo Mano de Obra Directa", "Costo Mano de Obra Indirecta", "Costos Indirectos de Fabricación"]:
        df_proc_calc[col] = pd.to_numeric(df_proc_calc[col], errors="coerce").fillna(0.0)
        
    df_proc_calc["Total ($/hr)"] = (
        df_proc_calc["Costo Mano de Obra Directa"] +
        df_proc_calc["Costo Mano de Obra Indirecta"] +
        df_proc_calc["Costos Indirectos de Fabricación"]
    )
    
    tarifas_dict = df_proc_calc.set_index("Proceso").to_dict(orient="index")
    
    st.markdown("#### 📊 Tarifas Totales Activas por Proceso ($/hr)")
    cols_proc = st.columns(4)
    for idx, row in df_proc_calc.iterrows():
        cols_proc[idx].metric(
            label=f"⚙️ {row['Proceso']}",
            value=f"${row['Total ($/hr)']:,.2f} / hr",
            delta=f"MOD: ${row['Costo Mano de Obra Directa']:.2f} | MOI: ${row['Costo Mano de Obra Indirecta']:.2f} | CIF: ${row['Costos Indirectos de Fabricación']:.2f}",
            delta_color="off"
        )

# Resumen en barra lateral
st.sidebar.divider()
st.sidebar.header("🏭 3. Tarifas por Proceso ($/hr)")
for proc_nombre, datos_p in tarifas_dict.items():
    st.sidebar.text(f"• {proc_nombre}: ${datos_p['Total ($/hr)']:,.2f}/hr")

# 4. MOTOR DE CÁLCULO GENERALIZABLE POR PRODUCTO Y METRAJE
def calcular_escenario_producto(prod_name, tipo, metros_orden):
    km_orden = metros_orden / 1000.0
    p_info = PRODUCTOS[prod_name]
    fases_n = p_info["fases"]
    neutros_n = p_info["neutros"]
    
    df_rec = st.session_state.mem_recetas[prod_name]
    df_tmp = st.session_state.mem_tiempos[prod_name]
    
    col_val = f"{tipo} (kg/km)"
    al_1350_fase = df_rec.loc[0, col_val]
    xlpe_fase = df_rec.loc[1, col_val]
    al_6201_neutro = df_rec.loc[2, col_val]
    xlpe_neutro = df_rec.loc[3, col_val]
    
    kg_km_1350 = al_1350_fase * fases_n
    kg_km_6201 = al_6201_neutro * neutros_n
    kg_km_xlpe = (xlpe_fase * fases_n) + (xlpe_neutro * neutros_n)
    
    tot_kg_1350 = kg_km_1350 * km_orden
    tot_kg_6201 = kg_km_6201 * km_orden
    tot_kg_xlpe = kg_km_xlpe * km_orden
    peso_total_kg = tot_kg_1350 + tot_kg_6201 + tot_kg_xlpe
    
    costo_tot_1350 = tot_kg_1350 * costo_al_1350
    costo_tot_6201 = tot_kg_6201 * costo_al_6201
    costo_tot_xlpe = tot_kg_xlpe * costo_xlpe
    costo_mp_total = costo_tot_1350 + costo_tot_6201 + costo_tot_xlpe
    
    col_t = f"{tipo} (hrs/km)"
    procesos_detalle = []
    horas_totales = 0.0
    tot_mod = 0.0
    tot_moi = 0.0
    tot_cif = 0.0
    costo_indirecto_total = 0.0
    
    for _, row in df_tmp.iterrows():
        proc = row["Proceso"]
        tarifas_p = tarifas_dict.get(proc, {"Costo Mano de Obra Directa": 0, "Costo Mano de Obra Indirecta": 0, "Costos Indirectos de Fabricación": 0, "Total ($/hr)": 0})
        
        hrs_proc = row[col_t] * km_orden
        c_mod = hrs_proc * tarifas_p["Costo Mano de Obra Directa"]
        c_moi = hrs_proc * tarifas_p["Costo Mano de Obra Indirecta"]
        c_cif = hrs_proc * tarifas_p["Costos Indirectos de Fabricación"]
        c_tot_proc = hrs_proc * tarifas_p["Total ($/hr)"]
        
        horas_totales += hrs_proc
        tot_mod += c_mod
        tot_moi += c_moi
        tot_cif += c_cif
        costo_indirecto_total += c_tot_proc
        
        procesos_detalle.append({
            "Proceso": proc,
            "Horas": hrs_proc,
            "Tarifa_Hr": tarifas_p["Total ($/hr)"],
            "MOD": c_mod,
            "MOI": c_moi,
            "CIF": c_cif,
            "Costo_Total_Proc": c_tot_proc
        })
        
    costo_gran_total = costo_mp_total + costo_indirecto_total
    costo_por_metro = costo_gran_total / metros_orden if metros_orden > 0 else 0.0
    
    df_mp = pd.DataFrame([
        {"Materia Prima": "ALAMBRE DE ALUMINIO 1350 9.50 MM H14", "Kg/Km Cable": kg_km_1350, "Consumo Total (kg)": tot_kg_1350, "Costo Total ($)": costo_tot_1350},
        {"Materia Prima": "ALAMBRE DE ALUMINIO 6201 3.00 MM", "Kg/Km Cable": kg_km_6201, "Consumo Total (kg)": tot_kg_6201, "Costo Total ($)": costo_tot_6201},
        {"Materia Prima": f"XLPE NEG ({fases_n} Fases + {neutros_n} Neutro)", "Kg/Km Cable": kg_km_xlpe, "Consumo Total (kg)": tot_kg_xlpe, "Costo Total ($)": costo_tot_xlpe},
    ])
    
    return {
        "df_mp": df_mp,
        "df_procesos": pd.DataFrame(procesos_detalle),
        "peso_total": peso_total_kg,
        "costo_mp": costo_mp_total,
        "horas_totales": horas_totales,
        "tot_mod": tot_mod,
        "tot_moi": tot_moi,
        "tot_cif": tot_cif,
        "costo_ind_total": costo_indirecto_total,
        "costo_total": costo_gran_total,
        "costo_metro": costo_por_metro,
        "kg_xlpe": tot_kg_xlpe,
        "costo_xlpe": costo_tot_xlpe
    }

act = calcular_escenario_producto(producto_sel, "Actual", metros)
comp = calcular_escenario_producto(producto_sel, "Compactado", metros)

diff_costo_tot = comp["costo_total"] - act["costo_total"]
diff_pct_tot = (diff_costo_tot / act["costo_total"]) * 100 if act["costo_total"] > 0 else 0
diff_xlpe_kg = comp["kg_xlpe"] - act["kg_xlpe"]
diff_xlpe_usd = comp["costo_xlpe"] - act["costo_xlpe"]
diff_horas = comp["horas_totales"] - act["horas_totales"]
diff_ind_tot = comp["costo_ind_total"] - act["costo_ind_total"]

# 5. TARJETAS DE IMPACTO EJECUTIVO (KPIs)
st.subheader(f"📊 Resultados de Simulación ({info_prod['nombre_corto']}) para {metros:,} metros ({km:,.2f} km)")

k1, k2, k3 = st.columns(3)
k1.metric(
    "💰 Costo Total: ACTUAL",
    f"${act['costo_total']:,.2f}",
    f"${act['costo_metro']:,.4f} / metro",
    delta_color="off"
)
k2.metric(
    "🚀 Costo Total: COMPACTADO",
    f"${comp['costo_total']:,.2f}",
    f"{diff_costo_tot:+,.2f} ({diff_pct_tot:+.2f}%)",
    delta_color="inverse"
)
k3.metric(
    "🛢️ Ahorro en XLPE NEG",
    f"{abs(diff_xlpe_kg):,.2f} kg",
    f"{diff_xlpe_usd:+,.2f} USD en aislamiento",
    delta_color="inverse"
)

st.markdown("")
t1, t2, t3, t4 = st.columns(4)
t1.metric(
    "⏱️ Tiempo Total: ACTUAL",
    f"{act['horas_totales']:,.2f} hrs",
    "Escenario Base",
    delta_color="off"
)
t2.metric(
    "⏱️ Tiempo Total: COMPACTADO",
    f"{comp['horas_totales']:,.2f} hrs",
    f"{diff_horas:+,.2f} hrs vs Actual",
    delta_color="inverse"
)
t3.metric(
    "🏭 Costo Indirecto: ACTUAL",
    f"${act['costo_ind_total']:,.2f}",
    "MOD + MOI + CIF Base",
    delta_color="off"
)
t4.metric(
    "🏭 Costo Indirecto: COMPACTADO",
    f"${comp['costo_ind_total']:,.2f}",
    f"{diff_ind_tot:+,.2f} USD vs Actual",
    delta_color="inverse"
)

st.divider()

# 6. PESTAÑA 2: COMPARATIVA DETALLADA DE TIEMPOS Y COSTOS INDIRECTOS
with tab2:
    st.markdown(f"### ⏱️ Comparativa por Proceso ({info_prod['nombre_corto']}): Tiempos Totales vs. Costos Indirectos Totales")
    
    df_comp_proc = pd.DataFrame({
        "Proceso": act["df_procesos"]["Proceso"],
        "Tarifa ($/hr)": act["df_procesos"]["Tarifa_Hr"],
        "Horas Actual": act["df_procesos"]["Horas"],
        "Horas Compactado": comp["df_procesos"]["Horas"],
        "Dif. Horas": comp["df_procesos"]["Horas"] - act["df_procesos"]["Horas"],
        "Costo Total Actual ($)": act["df_procesos"]["Costo_Total_Proc"],
        "Costo Total Compactado ($)": comp["df_procesos"]["Costo_Total_Proc"],
        "Dif. Costo ($)": comp["df_procesos"]["Costo_Total_Proc"] - act["df_procesos"]["Costo_Total_Proc"]
    })
    
    fila_total = pd.DataFrame([{
        "Proceso": "TOTAL GENERAL",
        "Tarifa ($/hr)": None,
        "Horas Actual": df_comp_proc["Horas Actual"].sum(),
        "Horas Compactado": df_comp_proc["Horas Compactado"].sum(),
        "Dif. Horas": df_comp_proc["Dif. Horas"].sum(),
        "Costo Total Actual ($)": df_comp_proc["Costo Total Actual ($)"].sum(),
        "Costo Total Compactado ($)": df_comp_proc["Costo Total Compactado ($)"].sum(),
        "Dif. Costo ($)": df_comp_proc["Dif. Costo ($)"].sum()
    }])
    
    df_comp_proc_final = pd.concat([df_comp_proc, fila_total], ignore_index=True)
    
    st.dataframe(
        df_comp_proc_final.style.format({
            "Tarifa ($/hr)": lambda x: f"${x:,.2f}" if pd.notnull(x) else "—",
            "Horas Actual": "{:,.2f} hrs",
            "Horas Compactado": "{:,.2f} hrs",
            "Dif. Horas": "{:+,.2f} hrs",
            "Costo Total Actual ($)": "${:,.2f}",
            "Costo Total Compactado ($)": "${:,.2f}",
            "Dif. Costo ($)": "${:+,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    st.markdown("#### 🧾 Desglose Acumulado por Elemento de Costo (MOD, MOI y CIF)")
    df_res_conv = pd.DataFrame([
        {"Rubro": "Costo Mano de Obra Directa (MOD)", "Actual ($)": act["tot_mod"], "Compactado ($)": comp["tot_mod"], "Diferencia ($)": comp["tot_mod"] - act["tot_mod"]},
        {"Rubro": "Costo Mano de Obra Indirecta (MOI)", "Actual ($)": act["tot_moi"], "Compactado ($)": comp["tot_moi"], "Diferencia ($)": comp["tot_moi"] - act["tot_moi"]},
        {"Rubro": "Costos Indirectos de Fabricación (CIF)", "Actual ($)": act["tot_cif"], "Compactado ($)": comp["tot_cif"], "Diferencia ($)": comp["tot_cif"] - act["tot_cif"]},
        {"Rubro": "TOTAL COSTOS INDIRECTOS Y MANO DE OBRA", "Actual ($)": act["costo_ind_total"], "Compactado ($)": comp["costo_ind_total"], "Diferencia ($)": comp["costo_ind_total"] - act["costo_ind_total"]},
    ])
    st.dataframe(
        df_res_conv.style.format({
            "Actual ($)": "${:,.2f}",
            "Compactado ($)": "${:,.2f}",
            "Diferencia ($)": "${:+,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

# 7. PESTAÑA 3: COMPARATIVA MATERIA PRIMA
with tab3:
    st.markdown(f"### Desglose de Materia Prima ({num_fases} Fases ASC + {num_neutros} Neutro AAAC)")
    
    df_comp_mp = pd.DataFrame({
        "Materia Prima": act["df_mp"]["Materia Prima"],
        "Actual (kg/km)": act["df_mp"]["Kg/Km Cable"],
        "Compactado (kg/km)": comp["df_mp"]["Kg/Km Cable"],
        "Consumo Actual (kg)": act["df_mp"]["Consumo Total (kg)"],
        "Consumo Compactado (kg)": comp["df_mp"]["Consumo Total (kg)"],
        "Costo Actual ($)": act["df_mp"]["Costo Total ($)"],
        "Costo Compactado ($)": comp["df_mp"]["Costo Total ($)"],
        "Diferencia ($)": comp["df_mp"]["Costo Total ($)"] - act["df_mp"]["Costo Total ($)"]
    })
    
    st.dataframe(
        df_comp_mp.style.format({
            "Actual (kg/km)": "{:,.2f}",
            "Compactado (kg/km)": "{:,.2f}",
            "Consumo Actual (kg)": "{:,.2f}",
            "Consumo Compactado (kg)": "{:,.2f}",
            "Costo Actual ($)": "${:,.2f}",
            "Costo Compactado ($)": "${:,.2f}",
            "Diferencia ($)": "${:+,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )

# 8. PESTAÑA 4: GRÁFICOS EJECUTIVOS E HISTÓRICO CONSOLIDADO (2024 - 2026)
with tab4:
    st.markdown(f"### 📊 Análisis Gráfico de la Orden Actual ({info_prod['nombre_corto']})")
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("**Costos Indirectos por Proceso ($): Actual vs. Compactado**")
        df_g_proc = pd.concat([
            act["df_procesos"][["Proceso", "Costo_Total_Proc"]].assign(Escenario="Actual"),
            comp["df_procesos"][["Proceso", "Costo_Total_Proc"]].assign(Escenario="Compactado")
        ])
        fig_proc = px.bar(
            df_g_proc, x="Proceso", y="Costo_Total_Proc", color="Escenario", barmode="group", text_auto=".2f",
            labels={"Costo_Total_Proc": "Costo Total ($)"},
            color_discrete_map={"Actual": "#EF553B", "Compactado": "#00CC96"}
        )
        fig_proc.update_layout(xaxis_title="", legend_title="")
        st.plotly_chart(fig_proc, use_container_width=True)

    with col_g2:
        st.markdown("**Tiempos Totales por Proceso (hrs): Actual vs. Compactado**")
        df_g_hrs = pd.concat([
            act["df_procesos"][["Proceso", "Horas"]].assign(Escenario="Actual"),
            comp["df_procesos"][["Proceso", "Horas"]].assign(Escenario="Compactado")
        ])
        fig_hrs = px.bar(
            df_g_hrs, x="Proceso", y="Horas", color="Escenario", barmode="group", text_auto=".2f",
            labels={"Horas": "Tiempo Total (hrs)"},
            color_discrete_map={"Actual": "#EF553B", "Compactado": "#00CC96"}
        )
        fig_hrs.update_layout(xaxis_title="", legend_title="")
        st.plotly_chart(fig_hrs, use_container_width=True)

    st.divider()
    
    # SECCIÓN HISTÓRICA CONSOLIDADA (2x50+50 + 3x50+50)
    st.markdown("### 📅 Simulación Histórica Consolidada (2024 – 2026): Ahorro Total (2x50+50 + 3x50+50)")
    st.markdown("Calcula automáticamente el ahorro generado usando los **tiempos y recetas guardados para cada producto**.")
    
    prod_2x50 = "CABLE PREENSAMBLADO ASC - AAAC 2 X 50 + 1 X 50 MM2"
    prod_3x50 = "CABLE PREENSAMBLADO ASC - AAAC 3 X 50 + 1 X 50 MM2"
    
    key_hist = "ed_hist_global"
    hist_edit = st.data_editor(
        st.session_state.mem_hist,
        key=key_hist,
        on_change=guardar_hist,
        args=(key_hist,),
        use_container_width=True,
        hide_index=True,
        disabled=["Año / Periodo"],
        column_config={
            "Año / Periodo": st.column_config.TextColumn("Periodo"),
            "Metros 2x50 + 50": st.column_config.NumberColumn("Metros 2x50 + 50 (m)", min_value=0, step=1000, format="%d"),
            "Metros 3x50 + 50": st.column_config.NumberColumn("Metros 3x50 + 50 (m)", min_value=0, step=1000, format="%d")
        }
    )
    
    filas_hist = []
    for _, row in st.session_state.mem_hist.iterrows():
        periodo = row["Año / Periodo"]
        m_2x50 = float(row["Metros 2x50 + 50"])
        m_3x50 = float(row["Metros 3x50 + 50"])
        
        act_2 = calcular_escenario_producto(prod_2x50, "Actual", m_2x50)
        comp_2 = calcular_escenario_producto(prod_2x50, "Compactado", m_2x50)
        ahorro_2 = act_2["costo_total"] - comp_2["costo_total"]
        ahorro_xlpe_kg_2 = act_2["kg_xlpe"] - comp_2["kg_xlpe"]
        
        act_3 = calcular_escenario_producto(prod_3x50, "Actual", m_3x50)
        comp_3 = calcular_escenario_producto(prod_3x50, "Compactado", m_3x50)
        ahorro_3 = act_3["costo_total"] - comp_3["costo_total"]
        ahorro_xlpe_kg_3 = act_3["kg_xlpe"] - comp_3["kg_xlpe"]
        
        ahorro_combinado = ahorro_2 + ahorro_3
        
        filas_hist.append({
            "Año / Periodo": periodo,
            "Metros 2x50+50": m_2x50,
            "Metros 3x50+50": m_3x50,
            "Metros Totales": m_2x50 + m_3x50,
            "Ahorro 2x50+50 ($)": ahorro_2,
            "Ahorro 3x50+50 ($)": ahorro_3,
            "AHORRO TOTAL COMBINADO ($)": ahorro_combinado,
            "XLPE Ahorrado Total (kg)": ahorro_xlpe_kg_2 + ahorro_xlpe_kg_3
        })
        
    df_hist_calc = pd.DataFrame(filas_hist)
    df_hist_calc["Ahorro Acumulado ($)"] = df_hist_calc["AHORRO TOTAL COMBINADO ($)"].cumsum()
    
    ahorro_tot_2x50 = df_hist_calc["Ahorro 2x50+50 ($)"].sum()
    ahorro_tot_3x50 = df_hist_calc["Ahorro 3x50+50 ($)"].sum()
    ahorro_gran_total = df_hist_calc["AHORRO TOTAL COMBINADO ($)"].sum()
    xlpe_gran_total = df_hist_calc["XLPE Ahorrado Total (kg)"].sum()
    
    h1, h2, h3, h4 = st.columns(4)
    h1.metric(
        "💵 AHORRO TOTAL COMBINADO (2024–2026)",
        f"${ahorro_gran_total:,.2f}",
        f"{df_hist_calc['Metros Totales'].sum():,.0f} metros totales",
        delta_color="normal"
    )
    h2.metric(
        "🔌 Ahorro Histórico 2x50 + 50",
        f"${ahorro_tot_2x50:,.2f}",
        f"{df_hist_calc['Metros 2x50+50'].sum():,.0f} m producidos",
        delta_color="off"
    )
    h3.metric(
        "🔌 Ahorro Histórico 3x50 + 50",
        f"${ahorro_tot_3x50:,.2f}",
        f"{df_hist_calc['Metros 3x50+50'].sum():,.0f} m producidos",
        delta_color="off"
    )
    h4.metric(
        "🛢️ XLPE NEG Total Ahorrado",
        f"{xlpe_gran_total:,.2f} kg",
        "Ambos calibres (2024–2026)",
        delta_color="off"
    )
    
    st.dataframe(
        df_hist_calc.style.format({
            "Metros 2x50+50": "{:,.0f} m",
            "Metros 3x50+50": "{:,.0f} m",
            "Metros Totales": "{:,.0f} m",
            "Ahorro 2x50+50 ($)": "${:,.2f}",
            "Ahorro 3x50+50 ($)": "${:,.2f}",
            "AHORRO TOTAL COMBINADO ($)": "${:,.2f}",
            "Ahorro Acumulado ($)": "${:,.2f}",
            "XLPE Ahorrado Total (kg)": "{:,.2f} kg"
        }),
        use_container_width=True,
        hide_index=True
    )
    
    col_h1, col_h2 = st.columns(2)
    
    with col_h1:
        st.markdown("**Ahorro Anual Combinado: 2x50+50 + 3x50+50 (USD)**")
        fig_stack = go.Figure()
        fig_stack.add_trace(go.Bar(
            x=df_hist_calc["Año / Periodo"],
            y=df_hist_calc["Ahorro 2x50+50 ($)"],
            name="2x50 + 1x50 mm²",
            marker_color="#00CC96",
            text=df_hist_calc["Ahorro 2x50+50 ($)"].apply(lambda x: f"${x:,.0f}"),
            textposition="inside"
        ))
        fig_stack.add_trace(go.Bar(
            x=df_hist_calc["Año / Periodo"],
            y=df_hist_calc["Ahorro 3x50+50 ($)"],
            name="3x50 + 1x50 mm²",
            marker_color="#636EFA",
            text=df_hist_calc["Ahorro 3x50+50 ($)"].apply(lambda x: f"${x:,.0f}"),
            textposition="inside"
        ))
        fig_stack.add_trace(go.Scatter(
            x=df_hist_calc["Año / Periodo"],
            y=df_hist_calc["AHORRO TOTAL COMBINADO ($)"],
            mode="text",
            text=df_hist_calc["AHORRO TOTAL COMBINADO ($)"].apply(lambda x: f"<b>Total: ${x:,.2f}</b>"),
            textposition="top center",
            showlegend=False
        ))
        fig_stack.update_layout(
            barmode="stack",
            yaxis_title="Ahorro Anual (USD)",
            legend_title="Calibre",
            yaxis=dict(range=[0, df_hist_calc["AHORRO TOTAL COMBINADO ($)"].max() * 1.18])
        )
        st.plotly_chart(fig_stack, use_container_width=True)
        
    with col_h2:
        st.markdown("**Curva de Ahorro Acumulado Combinado (2024 – 2026)**")
        fig_acum = px.area(
            df_hist_calc,
            x="Año / Periodo",
            y="Ahorro Acumulado ($)",
            markers=True,
            text=df_hist_calc["Ahorro Acumulado ($)"].apply(lambda x: f"${x:,.2f}"),
            color_discrete_sequence=["#00CC96"]
        )
        fig_acum.update_traces(textposition="top center")
        fig_acum.update_layout(
            xaxis_title="",
            yaxis_title="Ahorro Acumulado (USD)",
            yaxis=dict(range=[0, df_hist_calc["Ahorro Acumulado ($)"].max() * 1.18])
        )
        st.plotly_chart(fig_acum, use_container_width=True)
