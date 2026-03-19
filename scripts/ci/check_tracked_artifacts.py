from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ARTIFACTS_ROOT = PROJECT_ROOT / "artifacts"
ALLOWED_SUFFIXES = {".md"}


def main() -> int:
    result = subprocess.run(
        ["git", "ls-files", "--", "artifacts"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    tracked = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    prohibited: list[str] = []

    for rel_path in tracked:
        path = Path(rel_path)
        if not path.is_relative_to(Path("artifacts")):
            continue
        if path.suffix.lower() not in ALLOWED_SUFFIXES:
            prohibited.append(rel_path)

    if prohibited:
        print("Tracked operational artifacts are not allowed:")
        for rel_path in prohibited:
            print(f" - {rel_path}")
        print("Only Markdown documentation is allowed under artifacts/.")
        return 1

    print("Tracked artifacts policy passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
