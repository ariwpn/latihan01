import streamlit as st
import pandas as pd

st.title("📊 Data Makro Ekonomi Antar Negara")

df = pd.read_csv("data/macro_indicators_worldbank_2024.csv")

st.subheader("Tabel Data")
st.dataframe(
    df.style.format({
        "gdp_growth_pct": "{:.1f}",
        "inflation_cpi_pct": "{:.1f}",
        "unemployment_pct": "{:.1f}",
    }),
    use_container_width=True
)

st.subheader("Visualisasi Indikator")

# label tampil di UI -> kolom asli di data
indicator_map = {
    "GDP Growth (%)": "gdp_growth_pct",
    "Inflation CPI (%)": "inflation_cpi_pct",
    "Unemployment (%)": "unemployment_pct",
}

label = st.selectbox("Pilih indikator", list(indicator_map.keys()))
col = indicator_map[label]

st.bar_chart(df.set_index("country")[col])
