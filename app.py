import streamlit as st
import os
from backend import processar_lead, salvar_lead_csv

# Configura a API Key vinda dos Secrets do Streamlit
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

st.title("🚀 Qualificador de Leads Imobiliários")

texto_usuario = st.text_area("Cole a mensagem do lead aqui:")

if st.button("Analisar Lead"):
    if texto_usuario:
        with st.spinner('IA analisando...'):
            resultado = processar_lead(texto_usuario)
            salvar_lead_csv(resultado)
            
            st.success("Análise concluída!")
            st.metric("Score", resultado['score'])
            st.write(f"**Temperatura:** {resultado['temperatura']}")
            st.write(f"**Dossiê:** {resultado['dossie']}")
    else:
        st.warning("Por favor, digite algo.")