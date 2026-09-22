import streamlit as st

st.set_page_config(
    page_title="My Databricks App",
    page_icon="📊",
    layout="centered",
)

st.title("My Databricks App")
st.write("Hello P Databricks!")

name = st.text_input("Enter your name")

if name:
    st.success(f"Hello, {name}!")

st.divider()
st.write("This app is running with Python and Streamlit.")
