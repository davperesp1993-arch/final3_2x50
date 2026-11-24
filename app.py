import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Simulador Cable Preensamblado | Actual vs. Compactado",
    page_icon="⚡",
    layout="wide"
)

# ==============================================================================
# 1. VALORES PREDETERMINADOS DE FÁBRICA
# ==============================================================================
def get_default_recetas_2x50():
    return pd.DataFrame([
        {"Componente": "Fase ASC (x2) - Al 1350", "Actual (kg/km)": 135.97, "Compactado (kg/km)": 135.97},
        {"Componente": "Fase ASC (x2) - XLPE NEG", "Actual (kg/km)": 53.60, "Compactado (kg/km)": 41.00},
        {"Componente": "Neutro AAAC (x1) - Al 6201", "Actual (kg/km)": 134.17, "Compactado (kg/km)": 134.17},
        {"Componente": "Neutro AAAC (x1) - XLPE NEG", "Actual (kg/km)": 53.73, "Compactado (kg/km)": 53.73},
    ])

def get_default_recetas_3x50():
    return pd.DataFrame([
        {"Componente": "Fase ASC (x3) - Al 1350", "Actual (kg/km)": 135.97, "Compactado (kg/km)": 135.97},
        {"Componente": "Fase ASC (x3) - XLPE NEG", "Actual (kg/km)": 53.60, "Compactado (kg/km)": 41.00},
        {"Componente": "Neutro AAAC (x1) - Al 6201", "Actual (kg/km)": 134.17, "Compactado (kg/km)": 134.17},
        {"Componente": "Neutro AAAC (x1) - XLPE NEG", "Actual (kg/km)": 53.73, "Compactado (kg/km)": 53.73},
    ])

def get_default_tiempos():
    return pd.DataFrame([
        {"Proceso": "Trefilado", "Actual (hrs/km)": 1.00, "Compactado (hrs/km)": 0.85, "Detalle / Alcance": "Trefilado total de conductores"},
        {"Proceso": "Cableado", "Actual (hrs/km)": 2.27, "Compactado (hrs/km)": 2.52, "Detalle / Alcance": "Cableado normal vs. compactado"},
        {"Proceso": "Extrusado", "Actual (hrs/km)": 1.59, "Compactado (hrs/km)": 1.59, "Detalle / Alcance": "Aislamiento XLPE total"},
        {"Proceso": "Trenzado", "Actual (hrs/km)": 0.80, "Compactado (hrs/km)": 0.80, "Detalle / Alcance": "Reunido / Preensamblado final"},
    ])

def get_default_procesos():
    return pd.DataFrame([
        {
            "Proceso": "Trefilado",
            "Costo Mano de Obra Directa": 3.7560,
            "Costo Mano de Obra Indirecta": 6.1984,
            "Costos Indirectos de Fabricación": 6.6130
        },
        {
            "Proceso": "Cableado",
            "Costo Mano de Obra Directa": 4.4137,
            "Costo Mano de Obra Indirecta": 5.7342,
            "Costos Indirectos de Fabricación": 15.2870
        },
        {
            "Proceso": "Extrusado",
            "Costo Mano de Obra Directa": 4.6950,
            "Costo Mano de Obra Indirecta": 7.7480,
            "Costos Indirectos de Fabricación": 10.2380
        },
        {
            "Proceso": "Trenzado",
            "Costo Mano de Obra Directa": 7.5120,
            "Costo Mano de Obra Indirecta": 12.3968,
            "Costos Indirectos de Fabricación": 61.1548
        }
    ])

def get_default_historico():
    return pd.DataFrame([
        {"Periodo": "2024", "Metros 2x50 + 50": 697098, "Metros 3x50 + 50": 83765},
        {"Periodo": "2025", "Metros 2x50 + 50": 571272, "Metros 3x50 + 50": 62869},
        {"Periodo": "2026 (YTD)", "Metros 2x50 + 50": 411499, "Metros 3x50 + 50": 59976},
    ])

# ==============================================================================
# 2. INICIALIZACIÓN Y RESTABLECIMIENTO DE MEMORIA (SESSION STATE)
# ==============================================================================
def init_session_state(force_reset=False):
    if force_reset or "recetas_2x50" not in st.session_state:
        st.session_state.recetas_2x50 = get_default_recetas_2x50()
    if force_reset or "recetas_3x50" not in st.session_state:
        st.session_state.recetas_3x50 = get_default_recetas_3x50()
    if force_reset or "tiempos_2x50" not in st.session_state:
        st.session_state.tiempos_2x50 = get_default_tiempos()
    if force_reset or "tiempos_3x50" not in st.session_state:
        st.session_state.tiempos_3x50 = get_default_tiempos()
    if force_reset or "procesos_tarifas" not in st.session_state:
        st.session_state.procesos_tarifas = get_default_procesos()
    if force_reset or "historico_df" not in st.session_state:
        st.session_state.historico_df = get_default_historico()

    if force_reset:
        st.session_state.costo_al_1350 = 4.2700
        st.session_state.costo_al_6201 = 5.2416
        st.session_state.costo_xlpe = 2.2865
        st.session_state.metros_orden = 1000
        st.session_state.editor_version = st.session_state.get("editor_version", 0) + 1

if "editor_version" not in st.session_state:
    st.session_state.editor_version = 0

init_session_state(force_reset=False)

# ==============================================================================
# 3. ENCABEZADO Y BARRA LATERAL
# ==============================================================================
st.title("⚡ Simulador de Producción: Cable Preensamblado")

st.sidebar.header("🔌 1. Selección de Producto")
modelo_cable = st.sidebar.selectbox(
    "Calibre a simular:",
    [
        "CABLE PREENSAMBLADO ASC - AAAC 2 X 50 + 1 X 50 MM2",
        "CABLE PREENSAMBLADO ASC - AAAC 3 X 50 + 1 X 50 MM2"
    ]
)

es_3x50 = "3 X 50" in modelo_cable
num_fases = 3 if es_3x50 else 2
clave_modelo = "3x50" if es_3x50 else "2x50"

st.subheader(f"{modelo_cable} | Actual vs. Compactado")
st.markdown("Los tiempos, recetas y tarifas que edites se guardan automáticamente al cambiar de producto.")

st.sidebar.divider()
st.sidebar.header("📏 2. Orden de Producción")
metros = st.sidebar.number_input(
    "Cantidad a fabricar (Metros):",
    min_value=1,
    max_value=5000000,
    value=st.session_state.get("metros_orden", 1000),
    step=100,
    key="metros_orden"
)
km = metros / 1000.0
st.sidebar.caption(f"Equivalente a: **{km:,.3f} km**")

st.sidebar.divider()
st.sidebar.header("💲 3. Costos de Materia Prima ($/kg)")
costo_al_1350 = st.sidebar.number_input(
    "ALAMBRE DE ALUMINIO 1350 9.50 MM H14 ($/kg):",
    min_value=0.0,
    value=st.session_state.get("costo_al_1350", 4.2700),
    step=0.01,
    format="%.4f",
    key="costo_al_1350"
)
costo_al_6201 = st.sidebar.number_input(
    "ALAMBRE DE ALUMINIO 6201 3.00 MM ($/kg):",
    min_value=0.0,
    value=st.session_state.get("costo_al_6201", 5.2416),
    step=0.01,
    format="%.4f",
    key="costo_al_6201"
)
costo_xlpe = st.sidebar.number_input(
    "XLPE NEG ($/kg):",
    min_value=0.0,
    value=st.session_state.get("costo_xlpe", 2.2865),
    step=0.01,
    format="%.4f",
    key="costo_xlpe"
)

st.sidebar.divider()
if st.sidebar.button("🔄 Restablecer Valores Predeterminados", use_container_width=True, type="secondary"):
    init_session_state(force_reset=True)
    st.rerun()

st.divider()

# ==============================================================================
# 4. RECETAS PERSISTENTES POR MODELO
# ==============================================================================
v = st.session_state.editor_version
key_receta_state = f"recetas_{clave_modelo}"
key_tiempo_state = f"tiempos_{clave_modelo}"

with st.expander(f"📦 Ver / Editar Recetas de Materia Prima ({clave_modelo} - kg/km por conductor)", expanded=False):
    st.caption(f"Configuración unitaria por conductor. Las fases se multiplican automáticamente por **{num_fases}** y el neutro por **1**.")
    recetas_edit = st.data_editor(
        st.session_state[key_receta_state],
        hide_index=True,
        use_container_width=True,
        key=f"editor_rec_{clave_modelo}_v{v}"
    )
    st.session_state[key_receta_state] = recetas_edit

# ==============================================================================
# 5. PESTAÑAS PRINCIPALES
# ==============================================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🏭 Tiempos y Costos Indirectos (Modificable)",
    "⏱️ Comparativa Tiempos y Costos Totales",
    "📋 Comparativa Materia Prima", 
    "📈 Gráficos Ejecutivos e Histórico (2024–2026)"
])

# PESTAÑA 1: TIEMPOS Y COSTOS INDIRECTOS PERSISTENTES
with tab1:
    st.markdown(f"### ⏱️ 1. Tiempos Totales por Proceso para {clave_modelo} (hrs/km)")
    st.markdown("Edita los tiempos totales de cada proceso (`hrs/km`) para Actual y Compactado. Tus cambios quedan guardados en memoria.")
    
    tiempos_edit = st.data_editor(
        st.session_state[key_tiempo_state],
        use_container_width=True,
        hide_index=True,
        disabled=["Proceso"],
        key=f"editor_tiempos_{clave_modelo}_v{v}",
        column_config={
            "Proceso": st.column_config.TextColumn("Proceso"),
            "Actual (hrs/km)": st.column_config.NumberColumn("Tiempo Actual (hrs/km)", min_value=0.0, format="%.2f", required=True),
            "Compactado (hrs/km)": st.column_config.NumberColumn("Tiempo Compactado (hrs/km)", min_value=0.0, format="%.2f", required=True),
            "Detalle / Alcance": st.column_config.TextColumn("Observación")
        }
    )
    st.session_state[key_tiempo_state] = tiempos_edit

    st.divider()
    st.markdown("### 🏭 2. Costos Indirectos y Mano de Obra por Proceso ($/Hora-Máquina)")
    st.markdown("Edita los valores por hora para cada máquina. La columna **Total ($/hr)** se calcula automáticamente y aplica a ambos productos.")
    
    procesos_edit = st.data_editor(
        st.session_state.procesos_tarifas,
        use_container_width=True,
        hide_index=True,
        disabled=["Proceso"],
        key=f"editor_procesos_v{v}",
        column_config={
            "Proceso": st.column_config.TextColumn("Proceso / Línea"),
            "Costo Mano de Obra Directa": st.column_config.NumberColumn("Costo Mano de Obra Directa ($/hr)", min_value=0.0, format="$%.4f", required=True),
            "Costo Mano de Obra Indirecta": st.column_config.NumberColumn("Costo Mano de Obra Indirecta ($/hr)", min_value=0.0, format="$%.4f", required=True),
            "Costos Indirectos de Fabricación": st.column_config.NumberColumn("Costos Indirectos de Fabricación ($/hr)", min_value=0.0, format="$%.4f", required=True),
        }
    )
    st.session_state.procesos_tarifas = procesos_edit
    
    df_tarifas_calc = procesos_edit.copy()
    for col in ["Costo Mano de Obra Directa", "Costo Mano de Obra Indirecta", "Costos Indirectos de Fabricación"]:
        df_tarifas_calc[col] = pd.to_numeric(df_tarifas_calc[col], errors="coerce").fillna(0.0)
        
    df_tarifas_calc["Total ($/hr)"] = (
        df_tarifas_calc["Costo Mano de Obra Directa"] +
        df_tarifas_calc["Costo Mano de Obra Indirecta"] +
        df_tarifas_calc["Costos Indirectos de Fabricación"]
    )
    
    tarifas_dict = df_tarifas_calc.set_index("Proceso").to_dict(orient="index")
    
    st.markdown("#### 📊 Tarifas Totales Activas por Proceso ($/hr)")
    cols_proc = st.columns(4)
    for idx, row in df_tarifas_calc.iterrows():
        cols_proc[idx].metric(
            label=f"⚙️ {row['Proceso']}",
            value=f"${row['Total ($/hr)']:,.4f} / hr",
            delta=f"MOD: ${row['Costo Mano de Obra Directa']:.4f} | MOI: ${row['Costo Mano de Obra Indirecta']:.4f} | CIF: ${row['Costos Indirectos de Fabricación']:.4f}",
            delta_color="off"
        )

st.sidebar.divider()
st.sidebar.header("🏭 4. Tarifas Activas ($/hr)")
for proc_nombre, datos_p in tarifas_dict.items():
    st.sidebar.text(f"• {proc_nombre}: ${datos_p['Total ($/hr)']:,.4f}/hr")

# ==============================================================================
# 6. MOTOR DE CÁLCULO
# ==============================================================================
def calcular_escenario_modelo(tipo, km_calc, fases_n, df_rec, df_tiemp):
    col_val = f"{tipo} (kg/km)"
    
    al_1350_fase = float(df_rec.loc[0, col_val])
    xlpe_fase = float(df_rec.loc[1, col_val])
    al_6201_neutro = float(df_rec.loc[2, col_val])
    xlpe_neutro = float(df_rec.loc[3, col_val])
    
    kg_km_1350 = al_1350_fase * fases_n
    kg_km_6201 = al_6201_neutro * 1
    kg_km_xlpe = (xlpe_fase * fases_n) + (xlpe_neutro * 1)
    
    tot_kg_1350 = kg_km_1350 * km_calc
    tot_kg_6201 = kg_km_6201 * km_calc
    tot_kg_xlpe = kg_km_xlpe * km_calc
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
    
    for _, row in df_tiemp.iterrows():
        proc = row["Proceso"]
        tarifas_p = tarifas_dict.get(proc, {"Costo Mano de Obra Directa": 0, "Costo Mano de Obra Indirecta": 0, "Costos Indirectos de Fabricación": 0, "Total ($/hr)": 0})
        
        hrs_proc = float(row[col_t]) * km_calc
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
    metros_calc = km_calc * 1000.0
    costo_por_metro = costo_gran_total / metros_calc if metros_calc > 0 else 0
    
    df_mp = pd.DataFrame([
        {"Materia Prima": "ALAMBRE DE ALUMINIO 1350 9.50 MM H14", "Kg/Km Cable": kg_km_1350, "Consumo Total (kg)": tot_kg_1350, "Costo Total ($)": costo_tot_1350},
        {"Materia Prima": "ALAMBRE DE ALUMINIO 6201 3.00 MM", "Kg/Km Cable": kg_km_6201, "Consumo Total (kg)": tot_kg_6201, "Costo Total ($)": costo_tot_6201},
        {"Materia Prima": f"XLPE NEG ({fases_n} Fases + 1 Neutro)", "Kg/Km Cable": kg_km_xlpe, "Consumo Total (kg)": tot_kg_xlpe, "Costo Total ($)": costo_tot_xlpe},
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

act = calcular_escenario_modelo("Actual", km, num_fases, st.session_state[key_receta_state], st.session_state[key_tiempo_state])
comp = calcular_escenario_modelo("Compactado", km, num_fases, st.session_state[key_receta_state], st.session_state[key_tiempo_state])

diff_costo_tot = comp["costo_total"] - act["costo_total"]
diff_pct_tot = (diff_costo_tot / act["costo_total"]) * 100 if act["costo_total"] > 0 else 0
diff_xlpe_kg = comp["kg_xlpe"] - act["kg_xlpe"]
diff_xlpe_usd = comp["costo_xlpe"] - act["costo_xlpe"]
diff_horas = comp["horas_totales"] - act["horas_totales"]
diff_ind_tot = comp["costo_ind_total"] - act["costo_ind_total"]

# ==============================================================================
# 7. TARJETAS DE IMPACTO EJECUTIVO (KPIs)
# ==============================================================================
st.subheader(f"📊 Resultados de Simulación ({clave_modelo}) para {metros:,} metros ({km:,.2f} km)")

r1_c1, r1_c2, r1_c3 = st.columns(3)
r1_c1.metric("💰 Costo Total: ACTUAL", f"${act['costo_total']:,.2f}", f"${act['costo_metro']:,.4f} / metro", delta_color="off")
r1_c2.metric("🚀 Costo Total: COMPACTADO", f"${comp['costo_total']:,.2f}", f"{diff_costo_tot:+,.2f} USD ({diff_pct_tot:+.2f}%)", delta_color="inverse")
r1_c3.metric("🛢️ Ahorro XLPE NEG", f"{abs(diff_xlpe_kg):,.2f} kg", f"{diff_xlpe_usd:+,.2f} USD en aislamiento", delta_color="inverse")

st.markdown("")
r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
r2_c1.metric("⏱️ Tiempo Total: ACTUAL", f"{act['horas_totales']:,.2f} hrs", "Tiempo total de máquina", delta_color="off")
r2_c2.metric("⏱️ Tiempo Total: COMPACTADO", f"{comp['horas_totales']:,.2f} hrs", f"{diff_horas:+,.2f} hrs vs Actual", delta_color="inverse")
r2_c3.metric("🏭 Costo Indirecto: ACTUAL", f"${act['costo_ind_total']:,.2f}", "MOD + MOI + CIF Actual", delta_color="off")
r2_c4.metric("🏭 Costo Indirecto: COMPACTADO", f"${comp['costo_ind_total']:,.2f}", f"{diff_ind_tot:+,.2f} USD vs Actual", delta_color="inverse")

st.divider()

# ==============================================================================
# 8. CONTENIDO DE PESTAÑAS 2, 3 Y 4
# ==============================================================================
with tab2:
    st.markdown(f"### ⏱️ Comparativa por Proceso ({clave_modelo}): Tiempos vs. Costos Indirectos Totales")
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
    
    st.dataframe(
        pd.concat([df_comp_proc, fila_total], ignore_index=True).style.format({
            "Tarifa ($/hr)": lambda x: f"${x:,.4f}" if pd.notnull(x) else "—",
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
        df_res_conv.style.format({"Actual ($)": "${:,.2f}", "Compactado ($)": "${:,.2f}", "Diferencia ($)": "${:+,.2f}"}),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.markdown(f"### Desglose de Materia Prima ({num_fases} Fases ASC + 1 Neutro AAAC)")
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

with tab4:
    st.markdown("### 🏆 Impacto Histórico Consolidado (2024 – 2026): 2x50+50 + 3x50+50")
    st.markdown("Usa los parámetros guardados de cada calibre para calcular el ahorro total que se habría obtenido desde 2024.")
    
    hist_edit = st.data_editor(
        st.session_state.historico_df,
        use_container_width=True,
        hide_index=True,
        key=f"editor_hist_v{v}",
        column_config={
            "Periodo": st.column_config.TextColumn("Año / Periodo", required=True),
            "Metros 2x50 + 50": st.column_config.NumberColumn("Producción 2x50+50 (m)", min_value=0, step=100, format="%d", required=True),
            "Metros 3x50 + 50": st.column_config.NumberColumn("Producción 3x50+50 (m)", min_value=0, step=100, format="%d", required=True),
        }
    )
    st.session_state.historico_df = hist_edit
    
    act_1km_2x50 = calcular_escenario_modelo("Actual", 1.0, 2, st.session_state.recetas_2x50, st.session_state.tiempos_2x50)
    comp_1km_2x50 = calcular_escenario_modelo("Compactado", 1.0, 2, st.session_state.recetas_2x50, st.session_state.tiempos_2x50)
    ahorro_km_2x50 = act_1km_2x50["costo_total"] - comp_1km_2x50["costo_total"]
    
    act_1km_3x50 = calcular_escenario_modelo("Actual", 1.0, 3, st.session_state.recetas_3x50, st.session_state.tiempos_3x50)
    comp_1km_3x50 = calcular_escenario_modelo("Compactado", 1.0, 3, st.session_state.recetas_3x50, st.session_state.tiempos_3x50)
    ahorro_km_3x50 = act_1km_3x50["costo_total"] - comp_1km_3x50["costo_total"]
    
    filas_hist = []
    for _, row in hist_edit.iterrows():
        m_2x50 = float(row["Metros 2x50 + 50"])
        m_3x50 = float(row["Metros 3x50 + 50"])
        
        ah_2x50 = (m_2x50 / 1000.0) * ahorro_km_2x50
        ah_3x50 = (m_3x50 / 1000.0) * ahorro_km_3x50
        ah_total_anio = ah_2x50 + ah_3x50
        
        filas_hist.append({
            "Periodo": row["Periodo"],
            "Metros 2x50+50": m_2x50,
            "Metros 3x50+50": m_3x50,
            "Metros Totales": m_2x50 + m_3x50,
            "Ahorro 2x50+50 ($)": ah_2x50,
            "Ahorro 3x50+50 ($)": ah_3x50,
            "Ahorro Total Combinado ($)": ah_total_anio
        })
        
    df_hist_res = pd.DataFrame(filas_hist)
    df_hist_res["Ahorro Acumulado ($)"] = df_hist_res["Ahorro Total Combinado ($)"].cumsum()
    
    tot_m_comb = df_hist_res["Metros Totales"].sum()
    tot_ah_2x50 = df_hist_res["Ahorro 2x50+50 ($)"].sum()
    tot_ah_3x50 = df_hist_res["Ahorro 3x50+50 ($)"].sum()
    tot_ah_comb = df_hist_res["Ahorro Total Combinado ($)"].sum()
    
    st.markdown("")
    hk1, hk2, hk3, hk4 = st.columns(4)
    hk1.metric("📏 Metraje Total (2024–2026)", f"{tot_m_comb:,.0f} m", f"{tot_m_comb/1000:,.2f} km producidos", delta_color="off")
    hk2.metric("💵 Ahorro Total 2x50+50", f"${tot_ah_2x50:,.2f}", f"${ahorro_km_2x50:,.2f} / km", delta_color="off")
    hk3.metric("💵 Ahorro Total 3x50+50", f"${tot_ah_3x50:,.2f}", f"${ahorro_km_3x50:,.2f} / km", delta_color="off")
    hk4.metric("🏆 AHORRO TOTAL COMBINADO", f"${tot_ah_comb:,.2f}", "Suma 2x50+50 y 3x50+50 (2024–2026)", delta_color="normal")
    
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        st.markdown("**Ahorro Anual Combinado: 2x50+50 + 3x50+50 (USD)**")
        df_stack = pd.melt(
            df_hist_res,
            id_vars=["Periodo", "Ahorro Total Combinado ($)"],
            value_vars=["Ahorro 2x50+50 ($)", "Ahorro 3x50+50 ($)"],
            var_name="Producto",
            value_name="Ahorro ($)"
        )
        fig_stack = px.bar(
            df_stack, x="Periodo", y="Ahorro ($)", color="Producto", barmode="stack", text_auto=",.0f",
            color_discrete_map={"Ahorro 2x50+50 ($)": "#00CC96", "Ahorro 3x50+50 ($)": "#636EFA"}
        )
        fig_stack.add_trace(go.Scatter(
            x=df_hist_res["Periodo"], y=df_hist_res["Ahorro Total Combinado ($)"],
            text=[f"<b>Total: ${val:,.0f}</b>" for val in df_hist_res["Ahorro Total Combinado ($)"]],
            mode="text", textposition="top center", showlegend=False
        ))
        fig_stack.update_layout(xaxis_title="", yaxis_title="Ahorro Anual (USD)", legend_title="", yaxis=dict(range=[0, df_hist_res["Ahorro Total Combinado ($)"].max() * 1.18]))
        st.plotly_chart(fig_stack, use_container_width=True)
        
    with col_h2:
        st.markdown("**Evolución del Ahorro Acumulado Combinado (2024–2026)**")
        fig_acum = px.area(df_hist_res, x="Periodo", y="Ahorro Acumulado ($)", markers=True, text="Ahorro Acumulado ($)")
        fig_acum.update_traces(
            line_color="#00CC96", fillcolor="rgba(0, 204, 150, 0.2)",
            texttemplate="<b>$%{y:,.0f}</b>", textposition="top center"
        )
        fig_acum.update_layout(xaxis_title="", yaxis_title="Ahorro Acumulado (USD)", yaxis=dict(range=[0, tot_ah_comb * 1.18]))
        st.plotly_chart(fig_acum, use_container_width=True)

    st.markdown("#### 📋 Tabla Consolidada de Ahorro Histórico (2024 – 2026)")
    fila_tot_h = pd.DataFrame([{
        "Periodo": "TOTAL CONSOLIDADO",
        "Metros 2x50+50": df_hist_res["Metros 2x50+50"].sum(),
        "Metros 3x50+50": df_hist_res["Metros 3x50+50"].sum(),
        "Metros Totales": tot_m_comb,
        "Ahorro 2x50+50 ($)": tot_ah_2x50,
        "Ahorro 3x50+50 ($)": tot_ah_3x50,
        "Ahorro Total Combinado ($)": tot_ah_comb,
        "Ahorro Acumulado ($)": tot_ah_comb
    }])
    st.dataframe(
        pd.concat([df_hist_res, fila_tot_h], ignore_index=True).style.format({
            "Metros 2x50+50": "{:,.0f}",
            "Metros 3x50+50": "{:,.0f}",
            "Metros Totales": "{:,.0f}",
            "Ahorro 2x50+50 ($)": "${:,.2f}",
            "Ahorro 3x50+50 ($)": "${:,.2f}",
            "Ahorro Total Combinado ($)": "${:,.2f}",
            "Ahorro Acumulado ($)": "${:,.2f}"
        }),
        use_container_width=True,
        hide_index=True
    )
