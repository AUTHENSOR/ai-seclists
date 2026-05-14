# SIEGE: 10,010 Structured AI Failure Scenarios

SIEGE is a database of structured threat models for AI systems. Each scenario is a complete failure analysis: attack surface, trigger conditions, failure mode, harm assessment, detection difficulty, mitigations, and eval benchmark coverage gaps.

## Schema

| Field | Description |
|-------|-------------|
| `domain` | Healthcare, Finance, Government, Legal, Infrastructure, Education, Military/Defense, Social Services, Employment, Media, Consumer, Research |
| `attack_surface` | Mechanism by which the failure is triggered |
| `trigger_conditions` | Specific conditions required to produce the failure |
| `failure_mode` | Technical description of the resulting failure |
| `harm_type` | Physical, Financial, Legal, Societal, Epistemic, Psychological, Reputational, Existential |
| `harm_severity` | critical, high, medium, low |
| `detection_difficulty` | Estimated difficulty of detecting the failure in production |
| `eval_coverage` | Which benchmarks (HarmBench, TrustLLM, etc.) do and do not cover this scenario |
| `adversarial_variants` | Alternative attack vectors producing the same failure |
| `tags` | 24,000+ unique tags across all scenarios |

## Quick start

```bash
# Decompress the database (one-time, ~71MB)
gunzip -k siege.db.gz

# Query directly
sqlite3 siege.db "SELECT COUNT(*) FROM scenarios WHERE harm_severity='critical'"
# 4,479

# Healthcare scenarios
sqlite3 siege.db "SELECT title FROM scenarios WHERE domain='Healthcare' LIMIT 10"

# Scenarios with zero benchmark coverage
sqlite3 siege.db "SELECT title, domain FROM scenarios WHERE json_array_length(json_extract(eval_coverage, '$.covered_by')) = 0 LIMIT 10"
```

## Bridge to ai-seclists

The bridge script maps SIEGE scenarios to ai-seclists payload categories:

```bash
# Full run: payloads, coverage matrix, eval gaps, cross-references
python utils/siege-bridge.py

# Summary statistics
python utils/siege-bridge.py --stats

# Single domain
python utils/siege-bridge.py --domain Healthcare

# Coverage matrix only
python utils/siege-bridge.py --coverage-only

# Eval gap report
python utils/siege-bridge.py --eval-gaps

# CSV export
python utils/siege-bridge.py --export-csv scenarios.csv
```

## Summary

| Metric | Count |
|--------|-------|
| Scenarios | 10,010 |
| Domains | 12 |
| Critical severity | 4,479 |
| High severity | 4,984 |
| Harm types | 8 |
| Unique tags | 24,099 |

Every scenario includes eval coverage data identifying which major benchmarks fail to test for it.

## Integration with ai-seclists

The 6,500+ hand-curated payloads in ai-seclists test attack *techniques*. SIEGE scenarios describe failure *contexts*. Crossing them produces targeted test cases: does this injection technique trigger this specific failure mode in this domain?

Run `python utils/siege-bridge.py` to generate the full cross-reference.
