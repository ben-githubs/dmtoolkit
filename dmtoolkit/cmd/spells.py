import json
from pathlib import Path

from dmtoolkit.cmd._util import ConverterError, browser_fetch
from dmtoolkit.constants import ROOT_DIR
from dmtoolkit.api.models import Class, Subclass, ClassFeature, Entry
from dmtoolkit.api.serialize import dump_json, load_json


DEFAULT_RAW = ROOT_DIR /  "cmd/raw_spells.json"
DEFAULT_CONV = ROOT_DIR / "api" / "data" / "spells.json"

def fetch_spells(outfile: Path):
    # URLs to fetch
    urls = [
        "https://5e.tools/data/spells/spells-aag.json",
        "https://5e.tools/data/spells/spells-ai.json",
        "https://5e.tools/data/spells/spells-aitfr-avt.json",
        "https://5e.tools/data/spells/spells-egw.json",
        "https://5e.tools/data/spells/spells-ftd.json",
        "https://5e.tools/data/spells/spells-ftd.json",
        "https://5e.tools/data/spells/spells-idrotf.json",
        "https://5e.tools/data/spells/spells-llk.json",
        "https://5e.tools/data/spells/spells-phb.json",
        "https://5e.tools/data/spells/spells-scc.json",
        "https://5e.tools/data/spells/spells-tce.json",
        "https://5e.tools/data/spells/spells-xge.json",
        "https://5e.tools/data/spells/spells-tdcsr.json",
        "https://5e.tools/data/spells/spells-bmt.json",
        "https://5e.tools/data/spells/spells-sato.json",
        # "https://5e.tools/data/spells/spells-xphb.json"
    ]

    # Store info
    spells = []
    for url in urls:
        # Fetch the file
        data = browser_fetch(url)
        spells.append(json.loads(data))
    
    # Dump data in file
    with outfile.open("w") as f:
        json.dump(spells, f)

def convert(infile: Path, outfile: Path) -> list[Class]:
    pass