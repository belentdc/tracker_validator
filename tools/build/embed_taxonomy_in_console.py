#!/usr/bin/env python3
"""Re-embed the canonical taxonomy into the validation console.

The validation console (ndc_validation_console.html) ships with the taxonomy
baked in as a JavaScript constant so it runs fully offline. When the taxonomy
changes, run the taxonomy build first (taxonomy/build/build_taxonomy.py) and
then this script to refresh the console's embedded copy.

Usage:
    cd tools/build
    python3 embed_taxonomy_in_console.py

It reads taxonomy/ndc_taxonomy.json, derives the compact structure the console
needs (Category -> Purpose -> Instrument trees, target dimensions, adaptation
trees, benefits, and cross-cutting dimensions), and rewrites the `const TAX = ...`
line inside ndc_validation_console.html. Nothing else in the console is touched.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent           # tools/build/
TOOLS = HERE.parent                              # tools/
ROOT = TOOLS.parent                              # tracker/
TAX_JSON = ROOT / "taxonomy" / "ndc_taxonomy.json"
CONSOLE = TOOLS / "ndc_validation_console.html"

T = json.loads(TAX_JSON.read_text(encoding="utf-8"))


def compact():
    out = {}
    mit = T["domains"]["Mitigation"]
    cats = mit["Type of measure: category"]
    purps = mit["Type of measure: purpose"]
    insts = mit["Type of measure: instruments"]
    mit_tree = []
    for c in cats:
        pj = []
        for p in purps:
            if p["parent_1"] == c["code"]:
                ij = [{"label": i["label"], "code": i["code"]}
                      for i in insts if i["parent_2"] == p["code"]]
                pj.append({"label": p["label"], "code": p["code"], "instruments": ij})
        mit_tree.append({"label": c["label"], "code": c["code"], "purposes": pj})
    out["mitigation"] = mit_tree

    ada = T["domains"]["Adaptation"]
    ada_tree = []
    for c in ada["Category"]:
        mj = [{"label": m["label"], "code": m["code"]}
              for m in ada["Measure"] if m["parent_1"] == c["code"]]
        ada_tree.append({"label": c["label"], "code": c["code"], "measures": mj})
    out["adaptation"] = ada_tree

    tg = T["domains"]["Targets"]
    pick = lambda key: [{"label": r["label"], "code": r["code"]} for r in tg[key]]
    out["targets"] = {
        "area": pick("Target area"),
        "scope": pick("Target scope"),
        "ghg": pick("GHG target?"),
        "type": pick("Target type"),
        "conditionality": pick("Conditionality"),
        "ice": pick("ICE phase-out target type"),
    }

    out["benefits"] = [{"label": r["label"], "code": r["code"]}
                       for r in T["domains"]["Benefits"]["Type of benefit"]]

    cc = T["cross_cutting_dimensions"]
    out["mode"] = cc["mode"]["values"]
    out["geography"] = cc["geography"]["values"]
    out["activity"] = cc["activity"]["values"]
    out["asi"] = cc["asi"]["values"]
    out["status_of_measure"] = cc["status_of_measure"]["values"]
    return out


tax_js = json.dumps(compact(), ensure_ascii=False)
html = CONSOLE.read_text(encoding="utf-8")
new_html, n = re.subn(
    r"const TAX = \{.*?\};\nconst SAMPLE",
    "const TAX = " + tax_js + ";\nconst SAMPLE",
    html, count=1, flags=re.S,
)
if n != 1:
    raise SystemExit("Could not find the `const TAX = ...` block to replace. Aborting.")
CONSOLE.write_text(new_html, encoding="utf-8")
print("Re-embedded taxonomy into", CONSOLE.name,
      "—", len(compact()["mitigation"]), "mitigation categories,",
      len(compact()["adaptation"]), "adaptation categories.")
