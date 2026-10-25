# six-lens-research-review

Six-perspective scientific and engineering audit for security R&D, fuzzers, interpreters, code/commit reviews, and AI research agents.

The skill entrypoint is [`SKILL.md`](./SKILL.md). It works as a local skill for Claude Code (`~/.claude/skills/`) and Codex (`agents/openai.yaml`).

## Included

- six independent lenses: experimental science, runtime/domain semantics, mathematics/control theory, vulnerability/fuzzing mechanisms, statistics/causal inference, scientific-discovery-agent design
- validity gates G1-G6 (replay fidelity, observation/reachability, oracle integrity, algorithm/treatment fidelity, replication/causality, knowledge-update approval) with `PASS / FAIL / NOT_TESTED / NOT_APPLICABLE`
- evidence tiers (`CODE_VERIFIED`, `REPORTED_RESULT`, `INDEPENDENTLY_REPRODUCED`, `DERIVED`, `HYPOTHESIS`, `UNKNOWN`) and a separate conclusion-scope axis (`target-proven`, `lab-proven`, `hypothesis-only`)
- an issue write-back protocol that preserves preregistrations and records `INVALID/SUPERSEDED` instead of rewriting history
- `scripts/validate_record.py`: shape and required-gate checks for a small experiment record (not a verification of evidence truth)

## Related Skills

- [`security-hypothesis-lab`](https://github.com/windshock/security-hypothesis-lab) is the execution loop: question, facts, premises, hypothesis, exit rule, one next move. Use it to choose and run experiments, and use this skill to audit whether the results support the claim. Keep the executor and the auditor separate where possible.

## Use

Copy this folder into your local skills directory as `six-lens-research-review`, then ask for a six-lens cross-review (e.g. "6관점 교차 검토", "six-lens review of the latest commit").

## Validate

```text
python scripts/validate_record.py --self-test
python scripts/validate_record.py references/review-record.example.json
```
