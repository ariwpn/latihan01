import streamlit as st
import pandas as pd

st.set_page_config(page_title="Data Makro Ekonomi Antar Negara", page_icon="📊", layout="wide")

DATA_PATH = "data/macro_indicators_worldbank_latest.csv"

ASEAN_ISO3 = {"BRN", "KHM", "IDN", "LAO", "MYS", "MMR", "PHL", "SGP", "THA", "VNM"}

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip() for c in df.columns]

    # Normalisasi nama kolom kalau ternyata beda format
    rename_map = {
        "Country": "country",
        "countryiso3code": "iso3",
        "Country Code": "iso3",
        "gdp_growth_pct": "gdp_growth_pct",
        "inflation_cpi_pct": "inflation_cpi_pct",
        "unemployment_pct": "unemployment_pct",
        "gdp_growth_pct": "gdp_growth_pct",          # jaga-jaga kalau ada versi lain
        "inflation_cpi_pct": "inflation_cpi_pct",
        "unemployment_pct": "unemployment_pct",
    }
    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    # Pastikan numerik
    for c in ["gdp_growth_pct", "inflation_cpi_pct", "unemployment_pct"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df


st.title("📊 Data Makro Ekonomi Antar Negara")

# Load
try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(f"File tidak ketemu: {DATA_PATH}. Pastikan sudah ada di repo GitHub (di folder /data).")
    st.stop()

required = ["country", "iso3", "year", "gdp_growth_pct", "inflation_cpi_pct", "unemployment_pct"]
missing = [c for c in required if c not in df.columns]
if missing:
    st.error(
        "Kolom wajib tidak ada di CSV.\n\n"
        f"- Missing: {missing}\n"
        f"- Kolom tersedia: {list(df.columns)}\n\n"
        "Solusi: pastikan kamu membaca file `macro_indicators_worldbank_latest.csv` "
        "dan file itu yang terbaru dari script World Bank."
    )
    st.stop()

# Filter ASEAN
only_asean = st.checkbox("Tampilkan ASEAN saja", value=False)
if only_asean:
    df = df[df["iso3"].isin(ASEAN_ISO3)].copy()

# Interpretasi
def interpret(r):
    if pd.isna(r["gdp_growth_pct"]) or pd.isna(r["inflation_cpi_pct"]) or pd.isna(r["unemployment_pct"]):
        return "Data belum lengkap"

    g, i, u = r["gdp_growth_pct"], r["inflation_cpi_pct"], r["unemployment_pct"]

    g_txt = "Kontraksi" if g < 0 else ("Rendah" if g < 2 else ("Sedang" if g < 4 else "Tinggi"))
    i_txt = "Terkendali" if i < 3 else ("Sedang" if i < 6 else "Tinggi")
    u_txt = "Rendah" if u < 3 else ("Sedang" if u < 6 else "Tinggi")

    return f"GDP {g_txt} | Inflasi {i_txt} | Pengangguran {u_txt}"

df["interpretasi"] = df.apply(interpret, axis=1)

# Tabel
st.subheader("Tabel Data")

df_show = df[["country", "iso3", "year", "gdp_growth_pct", "inflation_cpi_pct", "unemployment_pct", "interpretasi"]]

st.dataframe(
    df_show.style.format({
        "gdp_growth_pct": "{:.1f}",
        "inflation_cpi_pct": "{:.1f}",
        "unemployment_pct": "{:.1f}",
    }),
    width="stretch",
)

# Visualisasi
st.subheader("Visualisasi Indikator")

indicator_map = {
    "GDP Growth (%)": "gdp_growth_pct",
    "Inflation CPI (%)": "inflation_cpi_pct",
    "Unemployment (%)": "unemployment_pct",
}

label = st.selectbox("Pilih indikator", list(indicator_map.keys()))
col = indicator_map[label]

plot_df = df[["country", col]].dropna().set_index("country")
st.bar_chart(plot_df, height=360)
