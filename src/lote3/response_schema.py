from pydantic import BaseModel, Field
from typing import Literal, Optional

class WriteFileIntent(BaseModel):
    """
    Contrato estrito para a intenção de mutação do Lote 3.
    Substitui o bash arbitrário por uma intenção estruturada determinística.
    """
    operation: Literal["WRITE_FILE_TEXT"] = Field(..., description="A operação a ser executada. Deve ser obrigatoriamente WRITE_FILE_TEXT.")
    target_path: str = Field(..., description="O caminho absoluto do arquivo a ser gravado.")
    content: str = Field(..., description="O conteúdo textual a ser gravado no arquivo.")
    explanation: Optional[str] = Field(None, description="Explicação opcional do raciocínio do modelo.")

    class Config:
        schema_extra = {
            "example": {
                "operation": "WRITE_FILE_TEXT",
                "target_path": "/tmp/aios_workspace/hello.txt",
                "content": "Hello AIOS Mutation",
                "explanation": "Criando arquivo de teste no workspace restrito."
            }
        }
