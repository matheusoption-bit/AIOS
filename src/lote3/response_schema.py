from pydantic import BaseModel, ConfigDict, Field
from typing import Literal, Optional

MAX_CONTENT_BYTES = 1_048_576

class WriteFileIntent(BaseModel):
    """
    Contrato estrito para a intenção de mutação do Lote 3.
    Substitui o bash arbitrário por uma intenção estruturada determinística.
    """
    operation: Literal["WRITE_FILE_TEXT"] = Field(..., description="A operação a ser executada. Deve ser obrigatoriamente WRITE_FILE_TEXT.")
    target_path: str = Field(..., description="O caminho absoluto do arquivo a ser gravado.")
    content: str = Field(..., max_length=MAX_CONTENT_BYTES, description="O conteúdo textual a ser gravado no arquivo.")
    explanation: Optional[str] = Field(None, description="Explicação opcional do raciocínio do modelo.")

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "operation": "WRITE_FILE_TEXT",
                "target_path": "/tmp/aios_workspace/outputs/hello.txt",
                "content": "Hello AIOS Mutation",
                "explanation": "Criando arquivo de teste no workspace restrito."
            }
        }
    )
