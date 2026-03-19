from pydantic import BaseModel, Field
from typing import Optional

class LLMResponse(BaseModel):
    """
    Contrato rígido para a resposta do modelo de linguagem no Lote 2.
    """
    command: str = Field(..., description="O comando shell a ser executado na sandbox.")
    explanation: Optional[str] = Field(None, description="Explicação opcional do raciocínio do modelo.")

    class Config:
        schema_extra = {
            "example": {
                "command": "echo 'Hello AIOS' > README.md",
                "explanation": "Criando um arquivo README de boas-vindas."
            }
        }
