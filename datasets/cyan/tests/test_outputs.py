"""Every evidence file under outputs/ parses and names when it was produced. No network."""

import json
from pathlib import Path

import pytest

OUTPUTS = Path(__file__).resolve().parents[1] / "outputs"


@pytest.mark.parametrize("path", sorted(OUTPUTS.glob("*.json")), ids=lambda p: p.name)
def test_output_parses_and_is_dated(path):
    rec = json.loads(path.read_text(encoding="utf-8"))
    stamp = rec.get("measured_at") or rec.get("searched_at")
    assert stamp and stamp.endswith("Z"), f"{path.name}: no UTC timestamp"
    assert path.stem.endswith(stamp[:10]), f"{path.name}: filename date differs from the stamp"
