import streamlit as st
import pandas as pd

st.title("📊 Data Makro Ekonomi Antar Negara")

df = pd.read_csv("data/macro_data.csv")

st.subheader("Tabel Data")
st.dataframe(df, use_container_width=True)

st.subheader("Visualisasi Indikator")
indikator = st.selectbox(
    "Pilih indikator",
    ["GDP_Growth", "Inflation", "Unemployment"]
)

st.bar_chart(df.set_index("Country")[indikator])
