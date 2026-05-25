import os
import json
import pandas as pd  # Importante: para ler o CSV
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# 1. Configuração
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-3.5-flash')

# 2. Schema
class LeadScoring(BaseModel):
    motivo_mudanca: str
    urgencia: str
    capacidade_financeira: str
    tags: List[str]

# 3. Função de Qualificação
def qualificar_lead(texto_usuario):
    # Dica: Você pode usar o schema aqui se quiser que a IA responda estruturada
    prompt = f"Analise o lead: '{texto_usuario}'. Retorne um JSON com 'score' (0-100), 'temperatura' (QUENTE/MORNO/FRIO) e 'analise'."
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)

# 4. Função de Recomendação (Versão Unificada e Otimizada)
def recomendar_imoveis(texto_usuario):
    # Leitura do CSV
    df = pd.read_csv("imoveis_sp.csv")
    
    # Filtro simples (Pega imóveis que tenham alguma palavra-chave do texto)
    palavras_chave = [p.lower() for p in texto_usuario.split() if len(p) > 3]
    if palavras_chave:
        mask = df['tags'].str.contains('|'.join(palavras_chave), na=False)
        candidatos = df[mask].head(20) # Limita a 20 para a IA não gastar tokens
    else:
        candidatos = df.head(10) # Fallback se não filtrar nada

    estoque_relevante = candidatos.to_json(orient='records')
    
    prompt = f"""
    Analise o desejo do cliente '{texto_usuario}' e sugira 4 imóveis da nossa base: {estoque_relevante}. 
    Retorne um JSON com uma lista de 'sugestoes', cada uma com 'titulo' e 'justificativa'.
    """
    
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)