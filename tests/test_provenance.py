"""Offline tests for the provenance helper."""

import hashlib

import pytest

from datasets._common import provenance


def test_code_provenance_hashes_sources_and_inputs(tmp_path):
    src = tmp_path / "a.py"
    src.write_text("print(1)\n", encoding="utf-8")
    inp = tmp_path / "manifest.jsonl"
    inp.write_text("{}\n", encoding="utf-8")
    rec = provenance.code_provenance([src, tmp_path / "absent.py"], [inp])
    assert rec["sources"][str(src)] == hashlib.sha256(b"print(1)\n").hexdigest()
    assert str(tmp_path / "absent.py") not in rec["sources"]
    assert rec["inputs"][str(inp)] == hashlib.sha256(b"{}\n").hexdigest()
    assert rec["base_revision"] is None or isinstance(rec["base_revision"], str)
    assert rec["working_tree_dirty"] in (True, False, None)


def test_write_new_refuses_to_overwrite(tmp_path):
    out = tmp_path / "outputs" / "result-2026-09-25T1701Z.json"
    provenance.write_new(out, "first\n")
    with pytest.raises(FileExistsError, match="never overwrites"):
        provenance.write_new(out, "second\n")
    assert out.read_text(encoding="utf-8") == "first\n"


def test_rel_keeps_paths_inside_the_repository_relative():
    assert provenance.rel(provenance.REPO_ROOT / "README.md") == "README.md"
