import streamlit as st
import pandas as pd

st.title("🏠 Home")

st.markdown("""
Selamat datang di dashboard perbandingan indikator ekonomi makro antar negara.
Gunakan sidebar untuk berpindah halaman.
""")

df = pd.read_csv("data/macro_indicators_worldbank_2024.csv")
st.subheader("Preview Data")
st.dataframe(df, use_container_width=True)
