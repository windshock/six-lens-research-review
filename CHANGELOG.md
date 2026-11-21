# Changelog

## 2026-11-21

### Added (validated via Experience Replay over 5 reviews, 0 false positives — php2shell project)

- **G7 "주장-산출물 대조" (claim-vs-artifact) gate**: verify a claimed update/result actually exists in the committed artifact (diff/file/content), not only in the commit message/handoff narrative; a binary/zip rebuild does not prove source was edited. Companion "서사 착시" failure pattern. (Caught the recurring class that slipped past 3 times before.)
- **Independent-reproduction as a standard G5 step**: every substantive review reproduces/cross-checks at least one committed artifact itself (fixture rerun, source diff, sha/byte match, external-source hash e.g. distro tarball sha256 vs official site); else mark "unverified at artifact level" and hold G5.
- **Defensive/public-artifact review checklist**: for guides, detection tools, vendor/public disclosure artifacts — public-artifact weaponization 0, vendor-report over-claim check, detection-rule efficacy axis (lab-replay ≠ real-traffic FP), vendor/public separation, the zip trap.
- **Meta-reflection mode**: cross-round (not single-round) synthesis — recurring miss patterns, registered-but-unclosed tracks, lessons captured-but-not-re-applied, open-item closure; event-driven triggers (same-failure ×3 / finding-conflict / N-no-candidate / post-release).

## 2026-10-25

### Added

- initial standalone release of the `six-lens-research-review` skill
- conclusion-scope axis (`target-proven / lab-proven / hypothesis-only`, vocabulary from `security-hypothesis-lab`), kept separate from evidence tiers
- exit rule with explicit invalid conditions before each query
- "scope illusion" failure pattern: lab-reproduced primitives reported as deployment impact
- executor/auditor separation section linking `security-hypothesis-lab`
- `validate_record.py`: optional `conclusion_scope` / `target_premises` checks (`target-proven` requires every target premise confirmed); self-test 10/10
