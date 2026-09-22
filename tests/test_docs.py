"""Documentation checks: relative links resolve, dated documents carry their date. No network."""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"\[[^\]]*\]\(([^)\s#]+)(?:#[^)]*)?\)")
ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
SKIP_DIRS = {
    ".venv",
    ".uv-cache",
    ".git",
    "data",
    "dist",
    ".pytest_cache",
    ".ruff_cache",
    "archive",
}
DATED_DIRS = ("docs/decisions", "docs/reviews", "docs/probes")


def markdown_files():
    for path in ROOT.rglob("*.md"):
        if not SKIP_DIRS & set(path.relative_to(ROOT).parts):
            yield path


def dated_files():
    for rel in DATED_DIRS:
        for path in sorted((ROOT / rel).glob("*.md")):
            if path.name != "README.md":
                yield path


@pytest.mark.parametrize("path", sorted(markdown_files()), ids=lambda p: str(p.relative_to(ROOT)))
def test_relative_links_resolve(path):
    broken = []
    for target in LINK.findall(path.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (path.parent / target).exists():
            broken.append(target)
    assert not broken, f"{path.relative_to(ROOT)}: {broken}"


@pytest.mark.parametrize("path", sorted(dated_files()), ids=lambda p: str(p.relative_to(ROOT)))
def test_dated_documents_carry_iso_date_in_first_heading(path):
    first = path.read_text(encoding="utf-8").splitlines()[0]
    assert first.startswith("# "), f"{path.relative_to(ROOT)}: first line is not a heading"
    assert ISO_DATE.search(first), f"{path.relative_to(ROOT)}: no ISO date in the first heading"


def test_dated_filenames_start_with_a_date_or_number():
    for path in dated_files():
        name = path.name
        assert ISO_DATE.match(name) or re.match(r"\d{4}-", name), name
