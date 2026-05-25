import os
import json
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List

# 1. Configuração
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-3.5-flash')

# 2. Estoque (Nome em MAIÚSCULO para importar corretamente)
ESTOQUE = [pd.read_csv("imoveis_sp.csv")
   
]

# 3. Schema
class LeadScoring(BaseModel):
    motivo_mudanca: str
    urgencia: str
    capacidade_financeira: str
    tags: List[str]

# 4. Função de Qualificação
def qualificar_lead(texto_usuario):
    prompt = f"""
    Analise o lead: '{texto_usuario}'. 
    Retorne um JSON com 'score' (0-100), 'temperatura' (QUENTE/MORNO/FRIO) e 'analise' (resumo).
    """
    # Exemplo de retorno simulado caso precise testar
    return {"score": 85, "temperatura": "QUENTE", "analise": "Cliente com alto potencial de compra."}

# 5. Função de Recomendação
def recomendar_imoveis(texto_usuario, estoque_disponivel):
    prompt = f"""
    Analise o desejo do cliente '{texto_usuario}' e sugira 4 imóveis do estoque: {json.dumps(estoque_disponivel)}. 
    Retorne um JSON com uma lista de 'sugestoes', cada uma com 'titulo' e 'justificativa'.
    """
    # Esta parte é a lógica que você já tinha, garantindo que o JSON seja retornado
    response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
    return json.loads(response.text)