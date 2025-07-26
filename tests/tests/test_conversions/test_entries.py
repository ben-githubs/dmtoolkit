from dataclasses import asdict
import json

import pytest

from dmtoolkit.api.models import Entry

from tests.constants import FIXTURE_DIR

with (FIXTURE_DIR / "entries.json").open("r") as f:
    FIXTURES = json.load(f)

@pytest.mark.parametrize("entry", tuple(FIXTURES.values()), ids=tuple(FIXTURES.keys()))
def test_entries(entry: dict):
    assert asdict(Entry.from_spec(entry["raw"])) == entry["result"]