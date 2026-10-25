# Changelog

## 2026-10-25

### Added

- initial standalone release of the `six-lens-research-review` skill
- conclusion-scope axis (`target-proven / lab-proven / hypothesis-only`, vocabulary from `security-hypothesis-lab`), kept separate from evidence tiers
- exit rule with explicit invalid conditions before each query
- "scope illusion" failure pattern: lab-reproduced primitives reported as deployment impact
- executor/auditor separation section linking `security-hypothesis-lab`
- `validate_record.py`: optional `conclusion_scope` / `target_premises` checks (`target-proven` requires every target premise confirmed); self-test 10/10
