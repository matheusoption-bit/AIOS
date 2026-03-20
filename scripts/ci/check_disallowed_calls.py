from __future__ import annotations

import ast
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SCAN_ROOTS = (
    PROJECT_ROOT / "src",
    PROJECT_ROOT / "infra",
    PROJECT_ROOT / "tests",
    PROJECT_ROOT / "scripts",
)
IGNORED_DIR_NAMES = {"venv", "__pycache__"}
ALLOWED_DISALLOWED_CALL_PATHS = {
    PROJECT_ROOT / "infra" / "sandbox" / "adapter.py",
    PROJECT_ROOT / "infra" / "sandbox" / "harness.py",
    PROJECT_ROOT / "src" / "lote2" / "lote2_runner.py",
    PROJECT_ROOT / "scripts" / "ci" / "check_tracked_artifacts.py",
    PROJECT_ROOT / "tests" / "integration" / "test_sandbox_containment.py",
    PROJECT_ROOT / "tests" / "test_adapter_hardening.py",
}
DISALLOWED_SUBPROCESS_FUNCS = {
    "Popen",
    "call",
    "check_call",
    "check_output",
    "getoutput",
    "getstatusoutput",
    "run",
}
DISALLOWED_OS_FUNCS = {
    "system",
    "popen",
    "execv",
    "execve",
    "execvp",
    "execvpe",
    "spawnl",
    "spawnle",
    "spawnlp",
    "spawnlpe",
    "spawnv",
    "spawnve",
    "spawnvp",
    "spawnvpe",
    "posix_spawn",
    "posix_spawnp",
}
DISALLOWED_BUILTINS = {
    "eval",
    "exec",
    "compile",
}
DISALLOWED_ADMIN_METHODS = {
    "copy_in",
    "run_command",
    "apply_mutation",
    "list_files",
    "read_file",
}


class ViolationCollector(ast.NodeVisitor):
    def __init__(self, path: Path) -> None:
        self.path = path
        self.violations: list[tuple[int, str]] = []
        self.subprocess_aliases: set[str] = set()
        self.os_aliases: set[str] = set()
        self.direct_subprocess_funcs: set[str] = set()
        self.direct_os_funcs: set[str] = set()
        self.importlib_aliases: set[str] = set()
        self.direct_import_module_funcs: set[str] = set()
        self.callable_aliases: dict[str, str] = {}

    @property
    def is_allowlisted(self) -> bool:
        return self.path in ALLOWED_DISALLOWED_CALL_PATHS

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "subprocess":
                self.subprocess_aliases.add(alias.asname or alias.name)
            if alias.name == "os":
                self.os_aliases.add(alias.asname or alias.name)
            if alias.name == "importlib":
                self.importlib_aliases.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module == "subprocess":
            for alias in node.names:
                imported_name = alias.asname or alias.name
                self.direct_subprocess_funcs.add(imported_name)
                if not self.is_allowlisted:
                    self.violations.append(
                        (node.lineno, "import from subprocess is not allowed")
                    )
        if node.module == "os":
            for alias in node.names:
                imported_name = alias.asname or alias.name
                if alias.name in DISALLOWED_OS_FUNCS:
                    self.direct_os_funcs.add(imported_name)
                    if not self.is_allowlisted:
                        self.violations.append(
                            (node.lineno, f"import from os for '{alias.name}' is not allowed")
                        )
        if node.module == "importlib":
            for alias in node.names:
                if alias.name == "import_module":
                    self.direct_import_module_funcs.add(alias.asname or alias.name)
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            target_name = node.targets[0].id
            value = node.value
            aliased_callable = None

            if isinstance(value, ast.Name):
                if value.id in DISALLOWED_BUILTINS:
                    aliased_callable = f"builtin '{value.id}'"
                elif value.id in self.direct_subprocess_funcs:
                    aliased_callable = f"subprocess function '{value.id}'"
                elif value.id in self.direct_os_funcs:
                    aliased_callable = f"os function '{value.id}'"
                elif value.id in self.callable_aliases:
                    aliased_callable = self.callable_aliases[value.id]
            elif isinstance(value, ast.Attribute) and isinstance(value.value, ast.Name):
                if value.value.id in self.os_aliases and value.attr in DISALLOWED_OS_FUNCS:
                    aliased_callable = f"os.{value.attr}"
                elif value.value.id in self.subprocess_aliases and value.attr in DISALLOWED_SUBPROCESS_FUNCS:
                    aliased_callable = f"subprocess.{value.attr}"

            if aliased_callable is None:
                self.callable_aliases.pop(target_name, None)
            else:
                self.callable_aliases[target_name] = aliased_callable

        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func

        if isinstance(func, ast.Name) and func.id in DISALLOWED_BUILTINS and not self.is_allowlisted:
            self.violations.append((node.lineno, f"builtin '{func.id}' is not allowed"))

        if isinstance(func, ast.Name) and func.id in self.callable_aliases and not self.is_allowlisted:
            self.violations.append(
                (
                    node.lineno,
                    f"aliased disallowed callable '{func.id}' -> {self.callable_aliases[func.id]} is not allowed",
                )
            )

        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id in self.os_aliases and func.attr in DISALLOWED_OS_FUNCS and not self.is_allowlisted:
                self.violations.append((node.lineno, f"os.{func.attr} is not allowed"))

            if (
                func.value.id in self.subprocess_aliases
                and func.attr in DISALLOWED_SUBPROCESS_FUNCS
                and not self.is_allowlisted
            ):
                self.violations.append(
                    (node.lineno, f"subprocess.{func.attr} is not allowed")
                )

            if (
                func.value.id in self.importlib_aliases
                and func.attr == "import_module"
                and len(node.args) >= 1
                and isinstance(node.args[0], ast.Constant)
                and node.args[0].value in {"os", "subprocess"}
                and not self.is_allowlisted
            ):
                self.violations.append(
                    (node.lineno, f"importlib.import_module('{node.args[0].value}') is not allowed")
                )

        if isinstance(func, ast.Name) and func.id in self.direct_subprocess_funcs and not self.is_allowlisted:
            self.violations.append(
                (node.lineno, f"subprocess function '{func.id}' is not allowed")
            )

        if isinstance(func, ast.Name) and func.id in self.direct_os_funcs and not self.is_allowlisted:
            self.violations.append(
                (node.lineno, f"os function '{func.id}' is not allowed")
            )

        if (
            isinstance(func, ast.Name)
            and func.id in self.direct_import_module_funcs
            and len(node.args) >= 1
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value in {"os", "subprocess"}
            and not self.is_allowlisted
        ):
            self.violations.append(
                (node.lineno, f"import_module('{node.args[0].value}') is not allowed")
            )

        if (
            isinstance(func, ast.Name)
            and func.id == "__import__"
            and len(node.args) >= 1
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value in {"os", "subprocess"}
            and not self.is_allowlisted
        ):
            self.violations.append(
                (node.lineno, f"__import__('{node.args[0].value}') is not allowed")
            )

        if (
            isinstance(func, ast.Call)
            and isinstance(func.func, ast.Name)
            and func.func.id == "getattr"
            and len(func.args) >= 2
            and isinstance(func.args[0], ast.Call)
            and isinstance(func.args[0].func, ast.Name)
            and func.args[0].func.id == "__import__"
            and len(func.args[0].args) >= 1
            and isinstance(func.args[0].args[0], ast.Constant)
            and func.args[0].args[0].value in {"os", "subprocess"}
            and isinstance(func.args[1], ast.Constant)
            and isinstance(func.args[1].value, str)
            and (
                func.args[1].value in DISALLOWED_OS_FUNCS
                or func.args[1].value in DISALLOWED_SUBPROCESS_FUNCS
            )
            and not self.is_allowlisted
        ):
            self.violations.append(
                (node.lineno, f"dynamic getattr import for '{func.args[1].value}' is not allowed")
            )

        if not self.is_allowlisted:
            if isinstance(func, ast.Attribute) and func.attr in DISALLOWED_ADMIN_METHODS:
                self.violations.append(
                    (node.lineno, f"runtime cannot call sandbox.{func.attr}() outside allowlist")
                )
            if isinstance(func, ast.Name) and func.id in DISALLOWED_ADMIN_METHODS:
                self.violations.append(
                    (node.lineno, f"runtime cannot call {func.id}() directly outside allowlist")
                )

        self.generic_visit(node)


def iter_python_files() -> list[Path]:
    files: list[Path] = []
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.py")):
            if any(part in IGNORED_DIR_NAMES for part in path.parts):
                continue
            files.append(path)
    return files


def main() -> int:
    violations: list[tuple[Path, int, str]] = []

    for path in iter_python_files():
        source = path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(path))
        except SyntaxError as exc:
            violations.append((path, exc.lineno or 1, f"syntax error during CI scan: {exc.msg}"))
            continue

        collector = ViolationCollector(path)
        collector.visit(tree)
        for lineno, message in collector.violations:
            violations.append((path, lineno, message))

    if violations:
        print("Disallowed calls found:")
        for path, lineno, message in violations:
            rel_path = path.relative_to(PROJECT_ROOT)
            print(f" - {rel_path}:{lineno}: {message}")
        return 1

    print("No disallowed shell or sandbox-admin calls found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
