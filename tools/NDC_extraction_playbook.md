# NDC Transport Tracker — Extraction Playbook

This is the reusable procedure for turning any NDC (or LTS) document into a validated set of transport-relevant database rows. It works in a fresh chat, in this project, or with any AI that can read the taxonomy and follow the schema.

The pipeline has three stages:

1. **Extract** — an AI (Claude now, the Policy Miner later) reads the document and produces a JSON extraction following the contract below.
2. **Validate** — you import that JSON into `ndc_validation_console.html`, review every row, correct classifications, split or delete rows, resolve flagged judgment calls, and confirm.
3. **Export** — the console produces a multi-sheet `.xlsx` matching the database, which you merge into the master tracker.

This document covers stage 1 (the extraction prompt) plus how it connects to stages 2–3.

---

## Files to keep in the project

Keep these three in the project so they are always available to attach:

- `ndc_taxonomy.json` — the canonical taxonomy. **Required for every extraction.** It is the authoritative list of valid Category → Purpose → Instrument values and their definitions.
- `ndc_validation_console.html` — the validation tool. Open it in a browser; it needs no install.
- `NDC_extraction_playbook.md` — this file.

Optional but useful: a recent copy of the tracker database (e.g. `giz-slocat-transport-tracker-database.xlsx`). Attaching it lets the AI mirror real classification conventions from existing rows, which improves consistency.

---

## How to run an extraction (exact steps)

1. Open a new chat in this project (or any new Claude chat).
2. Attach: (a) `ndc_taxonomy.json`, (b) the NDC PDF you want to process, and optionally (c) the database file.
3. Paste the entire prompt in the section **"EXTRACTION PROMPT — copy everything below the line"** below.
4. Claude returns a short summary followed by one `json` code block.
5. Copy the contents of that `json` block.
6. Open `ndc_validation_console.html`, click **Import JSON** (or paste into the box and click **Parse**), validate, then **Export to Excel**.
7. Merge the exported sheets into the master database. (Country-attribute columns — Annex I, Income Group, G20, region flags, GHG totals — are joined from your country table afterwards; the export does not fill them.)

---

## EXTRACTION PROMPT — copy everything below the line

---

You are an analyst for the GIZ–SLOCAT NDC Transport Tracker. Your task is to read the attached NDC (or LTS) document and extract every transport-relevant commitment, plus all economy-wide, energy, and net-zero targets, classifying each against the attached taxonomy and returning a single JSON object that the validation console can import.

**Before you start:** confirm `ndc_taxonomy.json` is attached. It is the authoritative source for all Category, Purpose, Instrument, and target-type values. If it is not attached, stop and ask for it. If a database file is attached, use existing rows as a guide to classification conventions.

### Core principles

- **Be over-inclusive, not precise.** It is far easier for the validator to delete a row than to discover a missing one. When a passage might be transport-relevant, extract it and set `flagged: true` with a note explaining the doubt. Never silently drop a borderline item.
- **Verbatim is sacred.** The `verbatim` field must be the exact text from the document in its original language (French, Spanish, English, etc.), copied character-for-character including any typos. Do not paraphrase, translate, or "clean up" the verbatim. This is what gets stored in the database and later verified against the source.
- **Always translate to English.** The `translation` field is always English, regardless of source language. It exists only so the validator can review classifications without re-reading the source language. It is not exported to the database.
- **Page numbers are required** on every row.

### Classification rules (these encode tracker conventions — follow them exactly)

1. **Generation rule.** Any NDC submitted since November 2024 is third-generation, regardless of the document's title or version number (a document called "NDC 3.0", "CDN 2.0 update", etc. is still 3rd-gen if submitted after that date). Record the submission date and note this in `meta.generationNote`.

2. **What to extract.**
   - All transport-specific mitigation measures and adaptation measures.
   - All **targets**, even non-transport ones: economy-wide GHG targets, energy-sector targets (renewables share, capacity, efficiency), and net-zero/carbon-neutrality targets. A document with no transport-specific target still yields target rows.
   - **Benefits / co-benefits** explicitly linked to a transport action (air quality, health, congestion, access, road safety, social inclusion, economic, SDGs).

3. **Conditionality on targets.** Assign `Conditional` or `Unconditional` **only when the specific target statement itself declares it**. Otherwise use `Unclear conditionality`. This matters: an energy or sector target usually does not state its own conditionality even when the country has an economy-wide conditional/unconditional split elsewhere — those stay `Unclear conditionality`.

4. **Split targets that carry an explicit split.** If one headline target states both an unconditional and a conditional share (e.g. "38% by 2030, of which 13% unconditional and 25% conditional"), emit **two rows**, one `Unconditional` and one `Conditional`. Each row's `verbatim` must be edited down to the portion specific to that share, not the whole sentence.

5. **Dual classification → repeated rows.** If one quote legitimately belongs in two categories, emit the same quote as two (or more) rows with different classifications. Flag each and note that it is a multi-classification twin.

6. **Bundled measures → split rows.** If one sentence contains two distinct measures (e.g. "purchase incentives and scrapping of old vehicles"), emit one row per measure, each with a `verbatim` trimmed to its own clause, and flag both.

7. **Adaptation with mitigation co-benefits → both domains.** If an adaptation measure states a mitigation co-benefit (e.g. an urban transport system whose stated benefit is transport-GHG reduction), emit it as an `adaptation` row **and** a `mitigation` row, and, if a co-benefit type fits, a `benefit` row. Note the twinning.

8. **Aspirational mentions that are not formal targets.** A passing reference to "carbon neutrality by 2050" inside a narrative about governance, with no committed scope or statement, is a judgment call, not a confirmed target. Include it but set `flagged: true`, set `confirmed`-relevant fields as best you can, and write a note saying it is a judgment call and the default is to reject. Let the human decide.

9. **Use only taxonomy values.** Every Category, Purpose, Instrument, target area, target type, adaptation measure, benefit, etc. must be an exact string from `ndc_taxonomy.json`. The hierarchy must be respected: an Instrument must belong to its Purpose, and a Purpose to its Category. If unsure which leaf fits, pick the closest and flag it.

10. **Mode and geography** are multi-select. Use `Mode: Not defined` / `Geography: Not defined` (or an empty list) when the document does not specify.

### Output schema

Return a short plain-text summary (row counts per domain, anything notable), then the complete extraction as a single `json` code block with exactly this shape:

```json
{
  "meta": {
    "documentId": "",
    "country": "Cameroon",
    "countryCode": "CMR",
    "typeOfDocument": "NDC",
    "documentName": "Third Generation NDC",
    "versionNumber": "NDC 3.0",
    "status": "Active",
    "date": "2025-10",
    "region": "Africa",
    "language": "fr",
    "generationNote": "Submitted Oct 2025 — 3rd generation per tracker rule (any submission since Nov 2024)."
  },
  "rows": [
    {
      "id": "r1",
      "domain": "target|mitigation|adaptation|benefit",
      "lang": "fr",
      "page": "23",
      "verbatim": "exact original-language text",
      "translation": "English translation",
      "fields": { },
      "confirmed": false,
      "flagged": false,
      "note": "",
      "source": "claude"
    }
  ]
}
```

Leave `documentId` blank (the human fills it). Set `countryCode` to the ISO-3166 alpha-3 code. Set `language` to the source language code. Set every row's `confirmed` to `false` and `source` to `"claude"`.

**`fields` content depends on `domain`:**

For `domain: "target"`:
```json
{ "area":"", "scope":"", "ghg":"", "type":"", "conditionality":"", "targetYear":"", "ice":"" }
```

For `domain: "mitigation"`:
```json
{ "category":"", "purpose":"", "instrument":"", "asi":"", "activity":"", "status":"", "mode":[], "geography":[] }
```

For `domain: "adaptation"`:
```json
{ "category":"", "measure":"", "activity":"", "mode":[], "geography":[] }
```

For `domain: "benefit"`:
```json
{ "benefit":"" }
```

### Controlled vocabularies (must match exactly; full Instrument list is in `ndc_taxonomy.json`)

**Targets**
- `area`: Net zero target | Overall mitigation target | Transport sector mitigation target | Transport sector adaptation target | Energy sector target
- `scope`: Overall mitigation target | Sector-wide | Subsector targets | Unclear scope
- `ghg`: GHG | Non-GHG
- `type`: GHG: Base year | GHG: BAU | GHG: Fixed level | GHG: Base year intensity | GHG: Trajectory | Other GHG targets | Renewable energy | Other non-GHG energy targets | Avoid targets | Mode share targets | Infrastructure targets | Vehicle efficiency targets | Zero emission vehicle targets | Biofuel targets | Renewable energy in transport targets | Non-national transport GHG mitigation target | Other non-GHG transport targets | General adaptation targets
- `conditionality`: Unconditional | Conditional | Unclear conditionality
- `ice` (only for ICE phase-out targets, else leave ""): Sales all vehicles | Sales cars | Sales public transport | Sales unclear scope | Fleet all vehicles | Fleet cars | Fleet public transport | Fleet unclear scope | Other ICE phase-out targets

**Mitigation — `category` then its allowed `purpose` values** (each purpose's `instrument` options are in the taxonomy file):
- Mode shift and demand management → Transport demand management; Economic conditions for sustainable transport; Digital solutions; Promote active mobility; Public transport improvement
- Transport system improvements → Enhance comprehensive transport planning; Improve infrastructure; Freight efficiency improvements; Education and behavioral change
- Energy efficiency → Promote vehicle improvements
- Electrification → Promote electric mobility
- Alternative fuels → Promote alternative fuels
- Aviation and maritime → Promote improvements in aviation; Promote improvements in shipping

**Adaptation — `category` then allowed `measure` values:**
- Structural and Technical → Transport Infrastructure Resilience; Transport System Adaptation; Risk assessment; Resilient transport technologies; Repair and maintenance
- Informational and Educational → Monitoring; Education and Training; Early warning & emergency planning
- Institutional and Regulatory → Transport Planning; Relocation; Redundancy; Transport adaptation regulation; Design Standards and updates
- Other adaptation and resilience measures → Other adaptation measures

**Cross-cutting**
- `asi`: Avoid | Shift | Improve | Avoid, shift | Avoid, improve | Shift, improve | Avoid, shift, improve
- `activity`: Not defined | Passenger transport | Freight | Both passenger and freight
- `status`: Implemented or adopted | Planned | Unclear
- `mode` (multi-select; parents and children both selectable): Mode: Not defined | Informal transport | Active mobility (Walking, Cycling) | Road (Two-/Three-wheelers, Cars, Private cars, Taxis, Truck, Bus) | Rail (Heavy rail, High-speed rail, Transit rail) | Water (Coastal shipping, Inland shipping, International maritime) | Aviation (Domestic aviation, International aviation)
- `geography` (multi-select): Geography: Not defined | Urban | Rural | Inter-city

**Benefits — `benefit`:** Air pollution reduction | Congestion reduction | Better social inclusion | Health Benefits | Improved accessibility | Road safety improvements | SDG referenced in NDC transport measures | Economic benefits

### Final checks before you output

- Every Instrument belongs to its stated Purpose, and every Purpose to its Category (verify against `ndc_taxonomy.json`).
- Every `verbatim` is exact original-language text; every `translation` is English.
- Targets with explicit conditional/unconditional splits are split into separate rows with share-specific verbatim.
- Borderline, bundled, dual-classified, and aspirational items are flagged with clear notes.
- The JSON is valid and in one `json` code block.

---

## End of extraction prompt

---

## Notes on the validator and downstream

- The validator (`ndc_validation_console.html`) reads exactly the JSON above. The cascading Category → Purpose → Instrument dropdowns enforce the hierarchy, so any classification slip in the extraction is easy to correct and impossible to re-enter wrongly by hand.
- Only `verbatim` is written to the Excel `Quote` / `Content` column. The `translation` is carried into a helper column for your reference and should be dropped before merging.
- The `source` field (`"claude"`, `"policy_miner"`, …) lets you tell which engine produced each row once you run more than one — useful for benchmarking the Policy Miner against Claude on the same document.
- When the Policy Miner is upgraded to emit this same JSON shape, nothing about the validator or this workflow changes — only the thing that produces the JSON changes.
