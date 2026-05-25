import streamlit as st
from backend import qualificar_lead, recomendar_imoveis

# --- OTIMIZAÇÃO: CACHE ---
@st.cache_data(ttl=3600)
def obter_resultado_completo(texto):
    qualificacao = qualificar_lead(texto)
    # CORREÇÃO 1: Removi a vírgula extra aqui
    recomendacoes = recomendar_imoveis(texto) 
    return {**qualificacao, "recomendacoes": recomendacoes}

# --- INTERFACE ---
st.set_page_config(page_title="Qualificador Imobiliário", layout="centered")
st.title("🚀 Qualificador de Leads Inteligente")
texto = st.text_area("Cole a mensagem do lead aqui:")

if st.button("Analisar Lead"):
    if texto:
        with st.spinner('O Concierge está analisando o pedido...'):
            try:
                # Processamento unificado
                res = obter_resultado_completo(texto)
                
                # Exibindo os resultados
                st.success("Análise concluída!")
                
                # Coluna de Score
                col1, col2 = st.columns(2)
                col1.metric("Score de Venda", res['score'])
                col2.write(f"**Temperatura:** {res['temperatura']}")
                
                st.markdown("---")
                st.write(f"**Análise do Gerente:** {res['analise']}")
                
                # Exibindo Recomendações
                st.subheader("Imóveis Sugeridos:")
                
                # CORREÇÃO 2: Acessando a chave 'sugestoes' que vem do JSON da IA
                for item in res['recomendacoes']['sugestoes']:
                    st.write(f"✅ **{item['titulo']}**")
                    st.write(f"💡 *{item['justificativa']}*")
                    
            except Exception as e:
                st.error(f"Erro ao processar: {e}")
    else:
        st.warning("Por favor, cole a mensagem do lead antes de analisar.")