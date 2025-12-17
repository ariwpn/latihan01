import streamlit as st
import pandas as pd

st.title("📊 Data Makro Ekonomi Antar Negara")

# === Load data (hasil script World Bank)
df = pd.read_csv("data/macro_indicators_worldbank_latest.csv")

# Pastikan kolom numerik
for c in ["gdp_growth_pct", "inflation_cpi_pct", "unemployment_pct"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")

# === Kolom interpretasi (ringkas)
def interpret(r):
    if pd.isna(r["gdp_growth_pct"]) or pd.isna(r["inflation_cpi_pct"]) or pd.isna(r["unemployment_pct"]):
        return "Data belum lengkap"
    g = r["gdp_growth_pct"]
    i = r["inflation_cpi_pct"]
    u = r["unemployment_pct"]

    if g < 0:
        g_txt = "Kontraksi"
    elif g < 2:
        g_txt = "Pertumbuhan rendah"
    elif g < 4:
        g_txt = "Pertumbuhan sedang"

st.subheader("Tabel Data")

st.dataframe(
    df[["country","iso3","year","gdp_growth_pct","inflation_cpi_pct","unemployment_pct","interpretasi"]]
      .style.format({
          "gdp_growth_pct": "{:.1f}",
          "inflation_cpi_pct": "{:.1f}",
          "unemployment_pct": "{:.1f}",
      }),
    width="stretch"
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

plot_df = df[["country", col]].dropna().set_index("country")
st.bar_chart(plot_df)

