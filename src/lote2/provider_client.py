import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Dict, Any, Tuple
from .response_schema import LLMResponse

# Carrega variáveis de ambiente
load_dotenv()

class OpenAIClient:
    """
    Módulo mínimo para chamada ao provider OpenAI fora da sandbox.
    """
    def __init__(self, model: str = "gpt-4o"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            # Não interrompemos aqui para permitir validação estática se as chaves faltarem
            print("[AVISO] OPENAI_API_KEY não encontrada no ambiente.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def get_completion(self, instruction: str) -> Tuple[str, LLMResponse]:
        """
        Envia instrução e exige saída em JSON compatível com LLMResponse.
        """
        if not self.api_key:
            raise ValueError(
                "ERRO: OPENAI_API_KEY não configurada. "
                "Crie um arquivo .env na raiz com sua chave para habilitar a execução real."
            )

        system_prompt = (
            "Você é o motor de decisão do AIOS. "
            "Sua resposta deve ser estritamente um JSON válido seguindo este schema: "
            "{'command': 'string', 'explanation': 'string'}. "
            "Não inclua markdown ou blocos de código na resposta final, apenas o JSON bruto."
        )

        try:
            print(f"[OpenAI] Solicitando completion (model={self.model})...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": instruction}
                ],
                response_format={"type": "json_object"}
            )

            raw_content = response.choices[0].message.content
            if not raw_content:
                raise ValueError("Resposta vazia recebida do provedor LLM.")

            print("[OpenAI] Resposta bruta recebida. Validando contra schema...")
            parsed_content = LLMResponse.model_validate_json(raw_content)
            
            return raw_content, parsed_content

        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha na integração OpenAI: {str(e)}")
            raise
