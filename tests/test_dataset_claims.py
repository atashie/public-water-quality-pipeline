"""Claim records under datasets/<name>/reference/ bind METADATA facts to checked quotes."""

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "datasets"
CLAIM_REF = re.compile(r"\[(cl-[a-z0-9_-]+)\]")
VERDICTS = {"confirmed", "corrected", "not_verifiable"}
STATUSES = {"documented", "probe"}


def research_files():
    return sorted(DATASETS.glob("*/reference/*-research.json"))


def checks_files():
    return sorted(DATASETS.glob("*/reference/*-checks.json"))


def metadata_files():
    return sorted(p for p in DATASETS.glob("*/METADATA.md") if p.parent.name != "_template")


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("path", research_files(), ids=lambda p: p.parent.parent.name)
def test_research_record_is_well_formed(path):
    rec = load(path)
    for key in ("dataset", "researcher", "sources", "claims", "not_found", "limitations"):
        assert key in rec, key
    source_ids = {s["id"] for s in rec["sources"]}
    assert len(source_ids) == len(rec["sources"]), "duplicate source id"
    for s in rec["sources"]:
        assert s["url"].startswith("https://") or s.get("local_copy"), s["id"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", s["accessed_on"]), s["id"]
    claim_ids = [c["id"] for c in rec["claims"]]
    assert len(set(claim_ids)) == len(claim_ids), "duplicate claim id"
    for c in rec["claims"]:
        assert c["id"].startswith(f"cl-{rec['dataset']}-"), c["id"]
        assert c["quote"].strip(), f"{c['id']}: empty quote"
        assert c["locator"].strip(), f"{c['id']}: empty locator"
        assert c["proposed_status"] in STATUSES, c["id"]
        assert c["source_ids"] and set(c["source_ids"]) <= source_ids, c["id"]


@pytest.mark.parametrize("path", checks_files(), ids=lambda p: p.parent.parent.name)
def test_checks_record_binds_to_research(path):
    checks = load(path)
    research = load(path.with_name(path.name.replace("-checks.json", "-research.json")))
    claim_ids = {c["id"] for c in research["claims"]}
    assert checks["checker"]["model"] != research["researcher"]["model"], (
        "same model checked itself"
    )
    seen = set()
    for chk in checks["checks"]:
        assert chk["claim_id"] in claim_ids, chk["claim_id"]
        assert chk["id"] == "chk-" + chk["claim_id"], chk["id"]
        assert chk["verdict"] in VERDICTS, chk["id"]
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", chk["checked_on"]), chk["id"]
        if chk["verdict"] in ("confirmed", "corrected"):
            assert chk["approved_value"] not in (None, ""), chk["id"]
            assert chk["quote"].strip(), chk["id"]
        seen.add(chk["claim_id"])
    assert seen == claim_ids, f"unchecked claims: {sorted(claim_ids - seen)}"


@pytest.mark.parametrize("path", metadata_files(), ids=lambda p: p.parent.name)
def test_metadata_documented_facts_cite_confirmed_claims(path):
    ref_dir = path.parent / "reference"
    research = {c["id"]: c for r in ref_dir.glob("*-research.json") for c in load(r)["claims"]}
    verdicts = {
        chk["claim_id"]: chk["verdict"]
        for f in ref_dir.glob("*-checks.json")
        for chk in load(f)["checks"]
    }
    missing, unconfirmed = [], []
    for claim_id in sorted(set(CLAIM_REF.findall(path.read_text(encoding="utf-8")))):
        if claim_id not in research:
            missing.append(claim_id)
        elif verdicts.get(claim_id) not in ("confirmed", "corrected"):
            unconfirmed.append(claim_id)
    assert not missing, f"cited but not in research: {missing}"
    assert not unconfirmed, f"cited but not confirmed: {unconfirmed}"
