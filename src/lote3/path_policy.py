from pathlib import PurePosixPath

WORKSPACE_ROOT = "/tmp/aios_workspace"
SAFE_WRITE_ROOT = f"{WORKSPACE_ROOT}/outputs"

class PathViolationError(Exception):
    """Exceção levantada quando uma tentativa de mutação escapa do workspace."""
    pass


def validate_safe_path(target_path: str) -> str:
    """
    Garante que o path resultante esteja contido ESTRITAMENTE dentro de
    SAFE_WRITE_ROOT (lógica Linux / E2B Sandbox).

    Regras:
    - Path vazio é rejeitado.
    - Path relativo é resolvido contra SAFE_WRITE_ROOT.
    - Path absoluto é aceito apenas se ficar dentro de SAFE_WRITE_ROOT.
    - Path traversal ('..') é neutralizado via PurePosixPath antes da checagem.
    - Sibling directories (/tmp/aios_workspace_hacker/) são rejeitados.

    Retorna o path canônico POSIX aceito, sem dupla barra.
    Lança PathViolationError nos demais casos.
    """
    if not target_path or not target_path.strip():
        raise PathViolationError("Path de destino não pode ser vazio.")

    workspace = PurePosixPath(SAFE_WRITE_ROOT)
    raw = PurePosixPath(target_path.strip())

    # Paths relativos são resolvidos dentro do workspace
    if not raw.is_absolute():
        candidate = workspace / raw
    else:
        candidate = raw

    # Canonicalizar: resolve '..' e '.' sem acesso a disco
    # PurePosixPath("/a/b/../c") == PurePosixPath("/a/c") não colapsa automaticamente,
    # então simplificamos via os.path.normpath (puramente léxico no POSIX)
    import posixpath
    canonical_str = posixpath.normpath(str(candidate))
    canonical = PurePosixPath(canonical_str)

    # Verificação de contenção hierárquica estrita
    if not canonical.is_relative_to(workspace):
        raise PathViolationError(
            f"Tentativa de path traversal ou escape bloqueada: "
            f"'{target_path}' resolve para '{canonical_str}' "
            f"que fica fora de '{SAFE_WRITE_ROOT}'."
        )

    return canonical_str
