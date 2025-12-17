import streamlit as st
import pandas as pd
import os

st.title("📈 Perbandingan Data Ekonomi Antar Negara")

PATH = "data/macro_indicators_worldbank_2024.csv"

if not os.path.exists(PATH):
    st.error(f"File tidak ditemukan: {PATH}. Pastikan CSV ada di folder data/ pada repo GitHub.")
    st.stop()

df = pd.read_csv(PATH)

# mapping label UI -> kolom data
indicator_map = {
    "GDP Growth (%)": "gdp_growth_pct",
    "Inflation CPI (%)": "inflation_cpi_pct",
    "Unemployment (%)": "unemployment_pct",
}

st.subheader("Pilih negara & indikator")
countries = st.multiselect(
    "Pilih negara",
    df["country"].unique().tolist(),
    default=df["country"].unique().tolist()[:3],
)

label = st.selectbox("Pilih indikator", list(indicator_map.keys()))
col = indicator_map[label]

dff = df[df["country"].isin(countries)].copy()

if dff.empty:
    st.warning("Tidak ada data untuk pilihan negara tersebut.")
    st.stop()

st.subheader("Grafik Perbandingan")
st.line_chart(dff.set_index("country")[col])

st.subheader("Interpretasi singkat")
max_row = dff.loc[dff[col].idxmax()]
min_row = dff.loc[dff[col].idxmin()]

st.write(
    f"Untuk indikator **{label}**, nilai tertinggi adalah **{max_row['country']}** "
    f"({max_row[col]:.1f}) dan nilai terendah adalah **{min_row['country']}** "
    f"({min_row[col]:.1f})."
)

with st.expander("Lihat data yang dipakai"):
    st.dataframe(dff, use_container_width=True)
