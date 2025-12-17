import streamlit as st
import pandas as pd

st.title("📈 Perbandingan Data Ekonomi Antar Negara")

df = pd.read_csv("data/macro_data.csv")

negara = st.multiselect(
    "Pilih negara",
    df["Country"].unique(),
    default=df["Country"].unique()[:3]
)

indikator = st.selectbox(
    "Pilih indikator",
    ["GDP_Growth", "Inflation", "Unemployment"]
)

df_filter = df[df["Country"].isin(negara)]

st.line_chart(df_filter.set_index("Country")[indikator])

st.markdown("""
**Interpretasi:**  
Perbedaan nilai indikator mencerminkan variasi kondisi ekonomi
antar negara yang dipilih.
""")
