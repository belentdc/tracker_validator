# NDC Transport Tracker

Tools and reference data for extracting, classifying, and validating transport-relevant commitments from Nationally Determined Contributions (NDCs) and Long-Term Strategies (LTS), feeding the GIZ–SLOCAT NDC Transport Tracker database.

This repository holds two things: the **taxonomy** that defines how commitments are classified, and the **tools** that turn a raw NDC document into validated, database-ready rows.

---

## The pipeline

```
NDC / LTS document
        │
        ▼
   1. EXTRACT      an AI (Claude now, the Policy Miner later) reads the document
                   and emits a JSON extraction following the contract in the playbook
        │
        ▼
   2. VALIDATE     you import that JSON into the validation console, review every
                   row against the taxonomy, correct, split, flag, and confirm
        │
        ▼
   3. EXPORT       the console produces a multi-sheet .xlsx matching the database,
                   which you merge into the master tracker
```

The extractor is swappable; the taxonomy and the validator are the stable core. Any AI that emits the agreed JSON shape works with the validator unchanged.

---

## Repository layout

```
tracker/
├── README.md                         this file
├── LICENSE
├── taxonomy/                         the classification reference
│   ├── README.md
│   ├── TAXONOMY.md                   human-readable, with Mermaid diagrams
│   ├── ndc_taxonomy.json             canonical machine-readable (feeds code / AI / validator)
│   ├── ndc_taxonomy.csv              flat version for spreadsheets
│   └── build/
│       ├── build_taxonomy.py         regenerates the three outputs from the workbook
│       ├── requirements.txt
│       └── NDC-taxonomy.xlsx         source of truth — edit this to change the taxonomy
└── tools/                            the working layer
    ├── README.md
    ├── ndc_validation_console.html   the validation tool (open in a browser)
    ├── NDC_extraction_playbook.md    the reusable extraction procedure + prompt
    ├── build/
    │   └── embed_taxonomy_in_console.py   refreshes the console's embedded taxonomy
    └── samples/
        └── cameroon_sample_extraction.json   worked example for testing
```

---

## Quick start

**To process an NDC:** follow `tools/NDC_extraction_playbook.md`. In short — attach `taxonomy/ndc_taxonomy.json` and the NDC PDF to a chat, paste the extraction prompt, copy the JSON it returns, open `tools/ndc_validation_console.html`, import the JSON, validate, and export to Excel.

**To see it work right now:** open `tools/ndc_validation_console.html` in a browser and click "Load Cameroon sample".

**To change the taxonomy:** edit `taxonomy/build/NDC-taxonomy.xlsx`, then regenerate everything:

```bash
cd taxonomy/build && pip install -r requirements.txt && python3 build_taxonomy.py
cd ../../tools/build && python3 embed_taxonomy_in_console.py
```

The first command rebuilds `ndc_taxonomy.json`, `ndc_taxonomy.csv`, and `TAXONOMY.md`. The second refreshes the copy of the taxonomy embedded in the validation console so its dropdowns stay in sync.

---

## How the pieces depend on each other

The workbook is the single source of truth. Everything else is generated from it:

```
NDC-taxonomy.xlsx
   │  build_taxonomy.py
   ├──────────────────────────►  ndc_taxonomy.json  (canonical)
   │                             ndc_taxonomy.csv
   │                             TAXONOMY.md
   │
ndc_taxonomy.json
   │  embed_taxonomy_in_console.py
   └──────────────────────────►  ndc_validation_console.html  (embedded copy)
```

The extraction playbook also points the AI at `ndc_taxonomy.json` as the authoritative classification list. So when the taxonomy changes, rerun both build steps and the whole pipeline stays consistent.

---

## License

Taxonomy and documentation are licensed CC BY 4.0. See `LICENSE`.

> GIZ and SLOCAT (2025). NDC Transport Tracker (vers. 4.0). Available from: www.changing-transport.org/tracker.

## Maintainers

- María Belén Vásquez — GIZ — maria.vasquez1@giz.de
- Nikola Medimorec — SLOCAT — nikola.medimorec@slocatpartnership.org
