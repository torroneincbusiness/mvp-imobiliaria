import os
import csv
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# 1. Configuração do Gemini
# Não precisa de drive, vamos apenas pegar a chave
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Estrutura de Dados
class LeadScoring(BaseModel):
    motivo_mudanca: str
    urgencia: str
    capacidade_financeira: str
    tags: List[str]

# 3. Regras de Negócio
PESOS = {
    "urgencia": {"alta": 50, "media": 25, "baixa": 10},
    "capacidade_financeira": {"alta": 40, "media": 20, "baixa": 5},
    "bonus_tag_premium": 10
}

estoque = [
    {"id": 1, "titulo": "Apto com Varanda Gourmet", "tags": ["varanda", "escritorio"], "preco": 450000},
    {"id": 2, "titulo": "Studio compacto", "tags": ["compacto"], "preco": 250000},
    {"id": 3, "titulo": "Cobertura Luxo", "tags": ["varanda", "piscina", "luxo"], "preco": 900000}
]

# 4. Funções
def processar_lead(texto_usuario):
    prompt = f"Analise o texto: '{texto_usuario}'. Extraia apenas o JSON seguindo o schema."
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json", "response_schema": LeadScoring}
    )
    dados = json.loads(response.text)

    sugestoes = [i for i in estoque if any(tag in i['tags'] for tag in dados['tags'])]
    score = PESOS['urgencia'].get(dados['urgencia'], 0) + PESOS['capacidade_financeira'].get(dados['capacidade_financeira'], 0)
    
    for tag in dados['tags']:
        if tag in ['luxo', 'cobertura']: score += PESOS['bonus_tag_premium']

    temperatura = "QUENTE" if score >= 80 else ("MORNO" if score >= 40 else "FRIO")
    
    return {
        "score": score,
        "temperatura": temperatura,
        "dossie": f"{dados['motivo_mudanca']} | Sugestões: {[s['titulo'] for s in sugestoes]}"
    }

def salvar_lead_csv(resultado_processamento, nome_arquivo="leads_imobiliaria.csv"):
    file_exists = os.path.isfile(nome_arquivo)
    with open(nome_arquivo, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=resultado_processamento.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(resultado_processamento)