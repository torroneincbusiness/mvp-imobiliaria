import streamlit as st
# Importa suas funções do seu arquivo backend
from backend import processar_lead, salvar_lead_csv, caminho_arquivo 

st.set_page_config(page_title="Qualificador de Leads", page_icon="🚀")

st.title("🚀 Qualificador de Leads Imobiliários")
st.write("Cole a mensagem do lead abaixo para classificar e salvar.")

# Entrada de dados
texto_usuario = st.text_area("Mensagem do Lead:", height=150)

if st.button("Analisar Lead"):
    if texto_usuario:
        with st.spinner('Analisando com IA...'):
            # Chama a lógica que já criamos
            resultado = processar_lead(texto_usuario)
            salvar_lead_csv(resultado, caminho_arquivo)
            
            # Exibe os resultados na tela
            st.success("Lead processado!")
            st.metric("Score", resultado['score'])
            st.info(f"**Temperatura:** {resultado['temperatura']}")
            st.write(f"**Dossiê:** {resultado['dossie']}")
    else:
        st.warning("Por favor, digite uma mensagem.")