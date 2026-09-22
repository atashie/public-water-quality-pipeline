"""Provenance of a run: which code produced a result and what it read.

A result file names the base Git revision, whether the working tree was dirty, the sha256 of
every source file involved, and the sha256 of every input file. A result produced by
uncommitted code is then still identifiable after the code changes.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from datasets._common.net import sha256_file

REPO_ROOT = Path(__file__).resolve().parents[2]


def _git(*args: str) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, timeout=30, check=False
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return out.stdout if out.returncode == 0 else None


def base_revision() -> str | None:
    """The short revision of HEAD, or None outside a Git checkout."""
    out = _git("rev-parse", "--short", "HEAD")
    return out.strip() if out else None


def working_tree_dirty() -> bool | None:
    """True when any tracked file is modified or any untracked file exists."""
    out = _git("status", "--porcelain")
    return bool(out.strip()) if out is not None else None


def rel(path: Path) -> str:
    path = Path(path).resolve()
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def code_provenance(sources: list[Path], inputs: list[Path] | None = None) -> dict:
    """Base revision, dirty flag, and sha256 of the named source and input files."""
    return {
        "base_revision": base_revision(),
        "working_tree_dirty": working_tree_dirty(),
        "sources": {rel(p): sha256_file(p) for p in sources if Path(p).is_file()},
        "inputs": {rel(p): sha256_file(p) for p in (inputs or []) if Path(p).is_file()},
    }
