import streamlit as st
import os
from backend import processar_lead

# O garçom busca a chave do cofre (Secrets)
# Se der erro aqui, verifique se no Streamlit Cloud, em 'Settings', 
# você adicionou a 'GOOGLE_API_KEY' na seção 'Secrets'.
os.environ["GOOGLE_API_KEY"] = st.secrets["GOOGLE_API_KEY"]

# --- OTIMIZAÇÃO: CACHE ---
# O cache impede que o site chame a IA várias vezes com a mesma pergunta,
# economizando sua cota da API e evitando o erro de "ResourceExhausted"
@st.cache_data(ttl=3600) 
def processar_lead_cached(texto):
    return processar_lead(texto)

# --- INTERFACE ---
st.title("🚀 Qualificador de Leads")
texto = st.text_area("Cole a mensagem do lead aqui:")

if st.button("Analisar Lead"):
    if texto:
        with st.spinner('IA analisando...'):
            try:
                # Chamamos a função que tem o cache
                resultado = processar_lead_cached(texto)
                
                # Exibindo os resultados
                st.success("Análise concluída!")
                st.metric("Score", resultado['score'])
                st.write(f"**Temperatura:** {resultado['temperatura']}")
                st.write(f"**Dossiê:** {resultado['dossie']}")
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar: {e}")
    else:
        st.warning("Por favor, cole a mensagem do lead antes de analisar.")