import streamlit as st
import os
from backend import processar_lead

# O garçom busca a chave do cofre (Secrets)
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

st.title("Qualificador de Leads")
texto = st.text_area("Cole a mensagem do lead:")

if st.button("Analisar"):
    resultado = processar_lead(texto)
    st.write(f"Score: {resultado['score']}")
    st.write(f"Dossiê: {resultado['dossie']}")