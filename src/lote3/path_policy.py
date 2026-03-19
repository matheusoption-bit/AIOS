import os
from pathlib import PurePosixPath

WORKSPACE_ROOT = "/tmp/aios_workspace"

class PathViolationError(Exception):
    """Exceção levantada quando uma tentativa de mutação escapa do workspace."""
    pass

def validate_safe_path(target_path: str) -> str:
    """
    Garante que o path absoluto resultante esteja contido estritamente
    dentro de WORKSPACE_ROOT Linux (PurePosixPath), já que a execução cai na E2B.
    Rejeita path traversal ('..') e aberturas relativas para cima.
    
    Retorna o path absoluto validado em formato UNIX ou levanta PathViolationError.
    """
    if not target_path:
        raise PathViolationError("Path de destino não pode ser vazio.")

    # Converte para Path POSIX
    p_target = PurePosixPath(target_path)
    
    # Se for relativo, ajeitamos contra a base
    if not p_target.is_absolute():
        p_target = PurePosixPath(WORKSPACE_ROOT) / p_target

    # Verifica travessias como /tmp/aios_workspace/../../etc/passwd
    # Em termos puramente léxicos (sem tocar em disco local):
    parts = p_target.parts
    resolved_parts = []
    
    for part in parts:
        if part == "..":
            if resolved_parts:
                resolved_parts.pop()
        elif part != "." and part != "":
            resolved_parts.append(part)
            
    # Remonta o caminho absoluto resolvido
    final_path = PurePosixPath("/".join(resolved_parts))
    if not str(final_path).startswith("/"):
        final_path = PurePosixPath("/" + str(final_path))

    workspace_path = PurePosixPath(WORKSPACE_ROOT)

    # Convert para string
    str_final = str(final_path)
    str_workspace = str(workspace_path)
    
    # Checa se o path cai perfeitamente dentro da raiz estipulada
    if not str_final.startswith(str_workspace):
         raise PathViolationError(f"Tentativa de path traversal bloqueada: '{target_path}' resolve para '{str_final}' que escapa de '{str_workspace}'.")

    return str_final
