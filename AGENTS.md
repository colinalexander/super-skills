# Repository instructions

This repository contains eight original, category-level agent skills synthesized from public evidence.

## Non-negotiable rules

- Do not copy, vendor, paraphrase closely, or commit third-party skill prose, code, examples, or assets.
- Treat `research/source-ledger.csv` as the authoritative provenance record.
- Preserve the CC BY 4.0 scope and GitSkills attribution for material under `research/`.
- Keep external raw material outside the repository. Use it only as transient research input.
- Record a source before using it as synthesis evidence.
- Add a synthesis-matrix entry for every retained principle, material conflict, or deliberate omission.
- Preserve the eight public skill boundaries in `research/SUITE_MANIFEST.md`.
- Prefer general decision rules over product-version-specific instructions. Verify current framework details from primary documentation when applying a skill.
- Do not introduce references to unrelated personal projects.

## Required checks

Run before sharing changes:

```bash
python3 scripts/validate_repository.py
```

Then run the host environment's official skill-creator quick validator against each `skills/<skill-name>` directory.

If a temporary corpus of raw source files is available outside this repository, also run:

```bash
python3 scripts/check_similarity.py --sources /absolute/path/to/raw-sources
```
