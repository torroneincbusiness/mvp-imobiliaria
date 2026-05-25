import os
import csv
import json
from typing import List
import google.generativeai as genai
from pydantic import BaseModel, Field

# --- 1. CONFIGURAÇÃO (O app.py definirá a chave no ambiente antes de chamar isso) ---
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-3.5-flash')

# --- 2. CONFIGURAÇÃO DE NEGÓCIO ---
PESOS = {
    "urgencia": {"alta": 50, "media": 25, "baixa": 10},
    "capacidade_financeira": {"alta": 40, "media": 20, "baixa": 5},
    "bonus_tag_premium": 10
}

# Em um futuro próximo, isso virá de um banco de dados real ou planilha
estoque = [
    {"id": 1, "titulo": "Apto com Varanda Gourmet", "tags": ["varanda", "escritorio"], "preco": 450000},
    {"id": 2, "titulo": "Studio compacto", "tags": ["compacto"], "preco": 250000},
    {"id": 3, "titulo": "Cobertura Luxo", "tags": ["varanda", "piscina", "luxo"], "preco": 900000}
]

# --- 3. ESQUEMA DE DADOS (Pydantic) ---
class LeadScoring(BaseModel):
    motivo_mudanca: str = Field(description="Resumo do evento de vida do usuário")
    urgencia: str = Field(description="Classificação: alta, media ou baixa")
    capacidade_financeira: str = Field(description="Classificação: alta, media ou baixa")
    tags: List[str] = Field(description="Interesses específicos, ex: varanda, pet-friendly")

# --- 4. FUNÇÕES PRINCIPAIS ---

def processar_lead(texto_usuario):
    """Analisa o lead, calcula score e retorna o dossiê."""
    prompt = f"Analise o texto: '{texto_usuario}'. Extraia os dados conforme o schema."
    
    response = model.generate_content(
        prompt,
        generation_config={
            "response_mime_type": "application/json",
            "response_schema": LeadScoring,
        },
    )
    
    dados = json.loads(response.text)

    # Lógica de Match
    sugestoes = [i for i in estoque if any(tag in i['tags'] for tag in dados['tags'])]

    # Cálculo de Score
    score = PESOS['urgencia'].get(dados['urgencia'], 0) + \
            PESOS['capacidade_financeira'].get(dados['capacidade_financeira'], 0)
    
    for tag in dados['tags']:
        if tag in ['luxo', 'cobertura']:
            score += PESOS['bonus_tag_premium']

    temperatura = "QUENTE" if score >= 80 else ("MORNO" if score >= 40 else "FRIO")

    return {
        "score": score,
        "temperatura": temperatura,
        "dossie": f"Motivo: {dados['motivo_mudanca']} | Sugestões: {[s['titulo'] for s in sugestoes]}"
    }

def salvar_lead_csv(resultado, nome_arquivo="leads.csv"):
    """Salva os dados em um CSV local."""
    arquivo_existe = os.path.isfile(nome_arquivo)
    
    with open(nome_arquivo, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=resultado.keys())
        if not arquivo_existe:
            writer.writeheader()
        writer.writerow(resultado)