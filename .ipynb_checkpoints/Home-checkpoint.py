import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Macroeconomic Overview",
    page_icon="📊",
    layout="wide",
)

DATA_PATH = "data/macro_indicators_worldbank_2024.csv"

@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    # basic sanity
    expected = {"country","iso3","year","gdp_growth_pct","inflation_cpi_pct","unemployment_pct"}
    missing = expected - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    return df

df = load_data(DATA_PATH)

# ===== Header =====
st.title("📊 Macroeconomic Overview")
st.caption("Ringkasan indikator ekonomi makro (World Bank – Most recent value).")

# ===== Sidebar controls =====
st.sidebar.header("Pengaturan")
year = st.sidebar.selectbox("Tahun", sorted(df["year"].unique(), reverse=True))
countries_default = ["Indonesia", "United States", "Japan", "China", "Germany"]
available = df["country"].unique().tolist()

selected_countries = st.sidebar.multiselect(
    "Pilih negara untuk ditampilkan",
    options=available,
    default=[c for c in countries_default if c in available],
)

focus_country = st.sidebar.selectbox(
    "Negara fokus (untuk interpretasi singkat)",
    options=selected_countries if selected_countries else available,
    index=0,
)

dff = df[(df["year"] == year) & (df["country"].isin(selected_countries))].copy()

if dff.empty:
    st.warning("Tidak ada data untuk pilihan ini. Cek file CSV atau pilihan negara.")
    st.stop()

# ===== KPI Cards =====
st.subheader(f"Ringkasan {year}")
focus = dff[dff["country"] == focus_country].iloc[0]
bench = dff[dff["country"] != focus_country]

bench_avg = bench[["gdp_growth_pct","inflation_cpi_pct","unemployment_pct"]].mean(numeric_only=True) if len(bench) else None

c1, c2, c3 = st.columns(3)

def delta_text(val, avg):
    if avg is None or pd.isna(avg):
        return None
    diff = val - avg
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.1f} vs avg peers"

with c1:
    st.metric(
        "GDP growth (annual %)",
        f"{focus['gdp_growth_pct']:.1f}%",
        delta_text(focus["gdp_growth_pct"], None if bench_avg is None else bench_avg["gdp_growth_pct"])
    )

with c2:
    st.metric(
        "Inflation, CPI (annual %)",
        f"{focus['inflation_cpi_pct']:.1f}%",
        delta_text(focus["inflation_cpi_pct"], None if bench_avg is None else bench_avg["inflation_cpi_pct"])
    )

with c3:
    st.metric(
        "Unemployment (%, ILO modeled)",
        f"{focus['unemployment_pct']:.1f}%",
        delta_text(focus["unemployment_pct"], None if bench_avg is None else bench_avg["unemployment_pct"])
    )

# ===== Charts =====
st.markdown("---")
st.subheader("Perbandingan cepat antar negara")

melt = dff.melt(
    id_vars=["country","iso3","year"],
    value_vars=["gdp_growth_pct","inflation_cpi_pct","unemployment_pct"],
    var_name="indicator",
    value_name="value"
)

indicator_labels = {
    "gdp_growth_pct": "GDP growth (annual %)",
    "inflation_cpi_pct": "Inflation, CPI (annual %)",
    "unemployment_pct": "Unemployment (% of labor force)"
}
melt["indicator"] = melt["indicator"].map(indicator_labels)

colA, colB = st.columns([1,1])

with colA:
    chosen_indicator = st.selectbox("Indikator", list(indicator_labels.values()), index=0)

with colB:
    sort_mode = st.selectbox("Urutkan", ["Tertinggi → Terendah", "Terendah → Tertinggi"], index=0)

plot_df = melt[melt["indicator"] == chosen_indicator].copy()
plot_df = plot_df.sort_values("value", ascending=(sort_mode == "Terendah → Tertinggi"))

fig = px.bar(
    plot_df,
    x="country",
    y="value",
    text="value",
    title=f"{chosen_indicator} ({year})",
)
fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
fig.update_layout(xaxis_title="", yaxis_title="", height=420)
st.plotly_chart(fig, use_container_width=True)

# ===== Interpretation =====
st.markdown("### Interpretasi singkat")
g = focus["gdp_growth_pct"]
inf = focus["inflation_cpi_pct"]
u = focus["unemployment_pct"]

notes = []
notes.append(f"- **Pertumbuhan** {focus_country} di **{g:.1f}%** (indikasi ekspansi ekonomi jika >0).")
notes.append(f"- **Inflasi** di **{inf:.1f}%** (lebih rendah umumnya berarti stabilitas harga lebih baik, tapi konteks kebijakan & permintaan tetap penting).")
notes.append(f"- **Pengangguran** di **{u:.1f}%** (lebih rendah biasanya menunjukkan pasar kerja lebih ketat).")

if bench_avg is not None and not bench_avg.isna().any():
    notes.append("")
    notes.append("**Dibanding rata-rata negara pembanding yang dipilih:**")
    notes.append(f"- GDP growth: {g:.1f}% vs rata-rata {bench_avg['gdp_growth_pct']:.1f}%")
    notes.append(f"- Inflasi: {inf:.1f}% vs rata-rata {bench_avg['inflation_cpi_pct']:.1f}%")
    notes.append(f"- Pengangguran: {u:.1f}% vs rata-rata {bench_avg['unemployment_pct']:.1f}%")

st.write("\n".join(notes))

with st.expander("Lihat tabel data"):
    st.dataframe(dff, use_container_width=True)

st.caption("Sumber: World Bank country data pages (most recent value).")
