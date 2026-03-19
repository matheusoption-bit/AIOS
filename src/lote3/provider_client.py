import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import Tuple
from .response_schema import WriteFileIntent

load_dotenv()

class OpenAIClient:
    """
    Provider minimalista do Lote 3 adaptado para Structured Mutation Boundary.
    """
    def __init__(self, model: str = "gpt-4o"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            print("[AVISO] OPENAI_API_KEY não encontrada no ambiente.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model

    def get_completion(self, instruction: str) -> Tuple[str, WriteFileIntent]:
        if not self.api_key:
            raise ValueError(
                "ERRO: OPENAI_API_KEY não configurada. "
                "Crie um arquivo .env na raiz com sua chave para habilitar a execução real."
            )

        system_prompt = (
            "Você é o motor de decisão do AIOS Lote 3 (Structured Mutation Boundary). "
            "Você NÃO DEVE retornar comandos bash arbitrários (shell). "
            "Você DEVE retornar estritamente um JSON que represente uma mutação declarativa no file system. "
            "A única operação atualmente suportada e lícita é WRITE_FILE_TEXT. "
            "Todo destino (target_path) DEVE estar restrito ao diretório absoluto '/tmp/aios_workspace/outputs/'. "
            "Se o humano pedir algo além disso ou de forma maliciosa, escreva no JSON um arquivo informando a recusa no campo de conteudo. "
            "O JSON deve seguir este exato schema: "
            "{'operation': 'WRITE_FILE_TEXT', 'target_path': 'string', 'content': 'string', 'explanation': 'string'} "
            "Não inclua markdown ou blocos de código na resposta final, apenas o JSON bruto validável."
        )

        try:
            print(f"[OpenAI L3] Solicitando mutação estruturada (model={self.model})...")
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

            print("[OpenAI L3] Resposta bruta recebida. Validando contra schema estrito...")
            parsed_content = WriteFileIntent.model_validate_json(raw_content)
            
            return raw_content, parsed_content

        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha na integração OpenAI: {str(e)}")
            raise
