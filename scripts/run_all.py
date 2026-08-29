"""Pipeline completo da análise — roda todos os módulos em ordem."""

from __future__ import annotations

import subprocess
import sys

MODULES = [
    "load",
    "etl",
    "revenue",
    "profile",
    "location",
    "drivers",
    "investment",
    "robustness",
]


def main() -> None:
    for m in MODULES:
        print(f"\n{'=' * 72}\n>>> invest.{m}\n{'=' * 72}")
        subprocess.run([sys.executable, "-m", f"invest.{m}"], check=True)


if __name__ == "__main__":
    main()
