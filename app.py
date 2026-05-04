"""App Streamlit para MVP comercial de clientes sin compra en abril 2026."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from src.analysis import build_churn_table
from src.data_loader import load_dataset
from src.telegram_alerts import build_telegram_messages, send_telegram_message
from src.utils import to_excel_bytes

st.set_page_config(page_title="MVP Sell-Out 2026", layout="wide")
st.title("📊 MVP Comercial: Clientes sin compra en abril 2026")

uploaded_file = st.file_uploader("Sube tu archivo CSV o Excel", type=["csv", "xlsx", "xls"])

if uploaded_file is None:
    st.info("Sube una base para iniciar el análisis.")
    st.stop()

try:
    raw_df = load_dataset(uploaded_file)
except Exception as exc:
    st.error(f"Error cargando archivo: {exc}")
    st.stop()

result_df = build_churn_table(raw_df)
if result_df.empty:
    st.warning("No se encontraron clientes que cumplan la lógica (compraron antes de abril y no en abril).")
    st.stop()

# Filtros
st.subheader("Filtros")
col1, col2, col3, col4 = st.columns(4)

bk_options = ["Todos"] + sorted(result_df["BK"].dropna().astype(str).unique().tolist())
priority_options = ["Todos"] + sorted(result_df["prioridad"].dropna().astype(str).unique().tolist())

# marca y subcategoría se obtienen desde el resumen calculado
all_brands = sorted(
    {
        b.strip()
        for brands in result_df["marcas_principales"].fillna("").astype(str)
        for b in brands.split(",")
        if b.strip()
    }
)
all_subcats = sorted(
    {
        s.strip()
        for subcats in result_df["subcategorias_principales"].fillna("").astype(str)
        for s in subcats.split(",")
        if s.strip()
    }
)

selected_bk = col1.selectbox("BK", bk_options)
selected_brand = col2.selectbox("Marca", ["Todos"] + all_brands)
selected_subcat = col3.selectbox("Subcategoría", ["Todos"] + all_subcats)
selected_priority = col4.selectbox("Prioridad", priority_options)

filtered = result_df.copy()
if selected_bk != "Todos":
    filtered = filtered[filtered["BK"] == selected_bk]
if selected_priority != "Todos":
    filtered = filtered[filtered["prioridad"] == selected_priority]
if selected_brand != "Todos":
    filtered = filtered[
        filtered["marcas_principales"].str.contains(selected_brand, case=False, na=False)
    ]
if selected_subcat != "Todos":
    filtered = filtered[
        filtered["subcategorias_principales"].str.contains(selected_subcat, case=False, na=False)
    ]

# KPIs
st.subheader("KPIs")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Clientes sin compra en abril", int(filtered["cliente_id"].nunique()))
k2.metric("NR histórico potencial (S/)", f"{filtered['nr_canje_historico'].sum():,.0f}")
k3.metric("Unidades históricas", f"{filtered['unidades_historicas'].sum():,.0f}")
k4.metric("Clientes alta prioridad", int((filtered["prioridad"] == "Alta").sum()))

st.subheader("Tabla priorizada")
show_cols = [
    "cliente_id",
    "nombre_cliente_real",
    "BK",
    "prioridad",
    "ultima_fecha_compra",
    "dias_desde_ultima_compra",
    "nr_canje_historico",
    "promedio_mensual_nr_canje",
    "unidades_historicas",
    "cantidad_compras_historicas",
    "skus_principales",
    "marcas_principales",
]

st.dataframe(filtered[show_cols], use_container_width=True)

st.download_button(
    label="📥 Descargar tabla en Excel",
    data=to_excel_bytes(filtered[show_cols]),
    file_name="clientes_sin_compra_abril_2026.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.subheader("Alertas Telegram")
messages = build_telegram_messages(filtered)
if not messages:
    st.info("No hay mensajes para el filtro seleccionado.")
else:
    for bk, msg in messages.items():
        with st.expander(f"Mensaje BK: {bk}", expanded=False):
            st.text_area("Texto generado", value=msg, height=320, key=f"msg_{bk}")
            if st.button(f"Enviar alerta BK {bk} a Telegram", key=f"send_{bk}"):
                ok, info = send_telegram_message(msg)
                if ok:
                    st.success(info)
                else:
                    st.warning(info)
