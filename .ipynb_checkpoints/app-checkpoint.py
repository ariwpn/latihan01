import streamlit as st

st.set_page_config(
    page_title="Women Economic Dashboard",
    layout="wide"
)

st.sidebar.title("Navigation")
st.sidebar.page_link("Home.py", label="Overview of Womens Data")
st.sidebar.page_link("Country_Profile.py", label="Country Profile")
st.sidebar.page_link("Comparison_between_Nations.py", label="Comparison between Nations")