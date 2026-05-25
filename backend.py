import os
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# 1. Configuração
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Estoque (Aqui você pode adicionar mais imóveis depois)
estoque = [
    {"id": 1, "titulo": "Apto com Varanda Gourmet", "tags": ["varanda", "escritorio"], "preco": 450000},
    {"id": 2, "titulo": "Studio compacto", "tags": ["compacto"], "preco": 250000},
    {"id": 3, "titulo": "Cobertura Luxo", "tags": ["varanda", "piscina", "luxo"], "preco": 900000}
]

# 3. Estrutura de Dados
class LeadScoring(BaseModel):
    motivo_mudanca: str
    urgencia: str
    capacidade_financeira: str
    tags: List[str]

# 4. Lógica Principal
def processar_lead(texto_usuario):
    # IA Extrai os dados
    prompt = f"Analise o texto: '{texto_usuario}'. Extraia os dados seguindo o schema."
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json", "response_schema": LeadScoring}
    )
    dados = json.loads(response.text)
    
    # Lógica de Match
    sugestoes = [i for i in estoque if any(tag in i['tags'] for tag in dados['tags'])]
    titulos = [s['titulo'] for s in sugestoes]
    
    # Cálculo de Score
    score = 0
    if dados['urgencia'] == "alta": score += 50
    if dados['capacidade_financeira'] == "alta": score += 40
    
    temperatura = "QUENTE" if score >= 80 else ("MORNO" if score >= 40 else "FRIO")
    
    return {
        "score": score,
        "temperatura": temperatura,
        "dossie": f"Motivo: {dados['motivo_mudanca']} | Sugestões: {', '.join(titulos) if titulos else 'Nenhuma sugestão encontrada'}"
    }