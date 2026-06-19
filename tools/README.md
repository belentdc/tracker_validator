# Tools

The working layer of the NDC Transport Tracker: how you turn a raw NDC document into validated, database-ready rows. The classification reference these tools depend on lives in `../taxonomy/`.

## Contents

| File | What it is |
|---|---|
| `NDC_extraction_playbook.md` | The reusable procedure and the full extraction prompt. Start here. |
| `ndc_validation_console.html` | The validation tool. Open in any browser — no install, works offline. |
| `samples/cameroon_sample_extraction.json` | A worked example (Cameroon CDN 3.0) for testing the console. |
| `build/embed_taxonomy_in_console.py` | Refreshes the taxonomy embedded in the console after a taxonomy change. |

## The workflow

1. Open a new chat. Attach `../taxonomy/ndc_taxonomy.json` and the NDC PDF.
2. Paste the extraction prompt from `NDC_extraction_playbook.md`.
3. Copy the JSON the AI returns.
4. Open `ndc_validation_console.html`, click **Import JSON**, and paste it (or use the **Parse** box).
5. Review every row: correct classifications via the dropdowns, split or delete rows, resolve flagged judgment calls, and **Confirm** each row.
6. Click **Export to Excel** and merge the sheets into the master database.

To see the console in action immediately, open it and click **Load Cameroon sample**.

## What the console does

- Four tabs — Targets, Mitigation, Adaptation, Benefits — each showing only its relevant columns.
- Verbatim quote (original language, exported) shown beside an English translation (validation only, not exported).
- Classification dropdowns populated from the taxonomy. The mitigation dropdowns cascade: Category filters Purpose, Purpose filters Instrument, so an invalid combination cannot be entered by hand.
- Mode and geography are multi-select with the parent/child structure from the taxonomy.
- Per-row controls: Confirm, Duplicate for second classification (for quotes that belong in two categories), Flag (with note), Delete.
- Export produces a multi-sheet `.xlsx` with mode/geography expanded to the `x`-marked columns matching the database, plus helper columns (translation, validated, flag note) you can drop before merging.

## Source-agnostic by design

The console reads a fixed JSON shape (documented in the playbook). It does not care whether Claude, the Policy Miner, or another tool produced the JSON — the `source` field on each row records which engine did. When the Policy Miner is upgraded to emit this shape, this workflow does not change; only the producer of the JSON changes.

## Keeping the console in sync with the taxonomy

The console ships with the taxonomy baked in so it runs offline. After any taxonomy change (see `../taxonomy/`), refresh the embedded copy:

```bash
cd build
python3 embed_taxonomy_in_console.py
```

This reads `../../taxonomy/ndc_taxonomy.json` and rewrites only the embedded taxonomy constant inside `ndc_validation_console.html`.

## Note on the export

The export fills the classification and per-document metadata columns. Country-attribute columns (Annex I / Non-Annex I, Income Group, G20, G7, OECD, EU27, region flags, GHG totals) are joined from your country table afterwards — the export leaves them out.
