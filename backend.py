import os
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# 1. Configuração
# Certifique-se de que a variável GOOGLE_API_KEY esteja configurada no Streamlit Cloud
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-3.5-flash')

# 2. Estoque de Imóveis (Normalize tudo para minúsculo aqui)
estoque = [
    {"id": 1, "titulo": "Apto com Varanda Gourmet", "tags": ["varanda", "escritorio"], "preco": 450000},
    {"id": 2, "titulo": "Studio compacto", "tags": ["compacto"], "preco": 250000},
    {"id": 3, "titulo": "Cobertura Luxo", "tags": ["varanda", "piscina", "luxo", "cobertura"], "preco": 900000}
]

# 3. Schema de Dados
class LeadScoring(BaseModel):
    motivo_mudanca: str
    urgencia: str
    capacidade_financeira: str
    tags: List[str]

# 4. Função Principal
def processar_lead(texto_usuario):
    
    # Prompt com "Few-Shot" (Aprendizado por exemplos)
    prompt = f"""
    Você é um assistente especialista em qualificação de leads imobiliários.
    Analise o texto do lead e extraia os dados estritamente seguindo o esquema JSON.

    Regras de Classificação:
    - Urgência 'alta': se mencionar "urgente", "logo", "agora", "este mês", "preciso rápido".
    - Urgência 'baixa': se mencionar "sem pressa", "só olhando", "futuramente".
    - Capacidade Financeira 'alta': se mencionar "orçamento bom", "tenho dinheiro", "investimento alto".
    
    Exemplos de Referência:
    - "Preciso comprar uma cobertura urgente": 
      {{ "motivo_mudanca": "compra", "urgencia": "alta", "capacidade_financeira": "media", "tags": ["cobertura"] }}
    - "Tenho orçamento alto e quero algo de luxo": 
      {{ "motivo_mudanca": "compra", "urgencia": "media", "capacidade_financeira": "alta", "tags": ["luxo"] }}

    Analise este lead agora: '{texto_usuario}'
    """

    try:
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json", "response_schema": LeadScoring}
        )
        dados = json.loads(response.text)
    except Exception as e:
        return {"score": 0, "temperatura": "ERRO", "dossie": f"Falha na IA: {str(e)}", "dados_extraidos": {}}

    # Normalização dos dados para garantir que o cálculo não falhe
    urgencia = dados.get('urgencia', '').lower().strip()
    financeiro = dados.get('capacidade_financeira', '').lower().strip()
    tags_lead = [t.lower().strip() for t in dados.get('tags', [])]
    
    # Cálculo de Score
    score = 0
    if "alta" in urgencia: score += 50
    elif "media" in urgencia: score += 25
    
    if "alta" in financeiro: score += 40
    elif "media" in financeiro: score += 20
    
    # Match de Tags (Busca exata no estoque)
    sugestoes = []
    for item in estoque:
        tags_item = [t.lower() for t in item['tags']]
        # Verifica se alguma tag do lead existe nas tags do imóvel
        if any(tag in tags_item for tag in tags_lead):
            sugestoes.append(item['titulo'])
            
    temperatura = "QUENTE" if score >= 80 else ("MORNO" if score >= 40 else "FRIO")
    
    return {
        "score": score,
        "temperatura": temperatura,
        "dados_extraidos": dados,
        "dossie": f"Motivo: {dados['motivo_mudanca']} | Sugestões: {', '.join(sugestoes) if sugestoes else 'Nenhuma'}"
    # --- Adicione esta nova função ---
def recomendar_imoveis(texto_usuario, estoque_disponivel):
    """
    Motor de Recomendação (Concierge)
    Focado apenas em cruzar o desejo do cliente com o estoque.
    """
    
    prompt = f"""
    Você é um corretor especializado. Analise o desejo do cliente: '{texto_usuario}'
    
    Estoque disponível para recomendação:
    {json.dumps(estoque_disponivel)}
    
    Sua missão:
    1. Selecione os 4 imóveis do estoque que melhor atendem ao que o cliente descreveu.
    2. Para cada um, escreva uma frase curta justificando por que ele é ideal.
    
    Retorne apenas um JSON:
    {{
        "sugestoes": [
            {{"titulo": "Nome do Imóvel", "justificativa": "Por que combina com o cliente?"}}
        ]
    }}
    """
    
    # Chama a API com o novo schema
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    return json.loads(response.text)