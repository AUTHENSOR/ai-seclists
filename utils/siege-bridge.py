#!/usr/bin/env python3
"""
AI SecLists: SIEGE Bridge

Maps the SIEGE database (10,010 structured AI failure scenarios) to
ai-seclists payloads. Generates scenario-derived payloads, coverage matrices,
and cross-reference indexes.

Usage:
    python utils/siege-bridge.py                          # full run, all outputs
    python utils/siege-bridge.py --domain healthcare      # single domain
    python utils/siege-bridge.py --coverage-only           # coverage matrix only
    python utils/siege-bridge.py --stats                   # summary statistics
    python utils/siege-bridge.py --export-csv scenarios.csv # export scenarios as CSV
"""

import argparse
import gzip
import json
import os
import re
import shutil
import sqlite3
import sys
import textwrap
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
SIEGE_DIR = REPO_ROOT / "siege"
SIEGE_DB_GZ = SIEGE_DIR / "siege.db.gz"
SIEGE_DB = SIEGE_DIR / "siege.db"
OUTPUT_DIR = REPO_ROOT / "siege" / "generated"

DOMAIN_MAP = {
    "Healthcare": "healthcare",
    "Finance": "finance",
    "Government": "government",
    "Legal": "legal",
    "Infrastructure": "infrastructure",
    "Education": "education",
    "Military/Defense": "military-defense",
    "Social Services": "social-services",
    "Employment": "employment",
    "Media": "media",
    "Consumer": "consumer",
    "Research": "research",
    "Cross-Domain": "cross-domain",
}

CATEGORY_TAG_MAP = {
    "prompt-injection": [
        "prompt-injection", "injection", "instruction-override", "delimiter",
        "context-manipulation", "adversarial-prompt", "system-prompt",
        "indirect-injection", "context-overflow",
    ],
    "jailbreaks": [
        "jailbreak", "roleplay", "hypothetical", "DAN", "persona",
        "refusal-suppression", "safety-bypass", "alignment-bypass",
        "role-assumption", "fictional-framing",
    ],
    "tool-abuse": [
        "tool-abuse", "API", "SSRF", "command-injection", "SQL-injection",
        "path-traversal", "parameter-injection", "tool-manipulation",
        "function-call", "privilege-escalation",
    ],
    "exfiltration": [
        "exfiltration", "data-leak", "prompt-leak", "extraction",
        "side-channel", "steganographic", "covert-channel",
    ],
    "memory-poisoning": [
        "memory-poisoning", "context-poisoning", "persistence",
        "sleeper", "gradual-drift", "cross-session",
    ],
    "agent-manipulation": [
        "agent", "goal-hijacking", "multi-agent", "planning-manipulation",
        "observation-poisoning", "tool-confusion", "reward-hacking",
        "objective-misalignment",
    ],
    "rag-poisoning": [
        "RAG", "retrieval", "document-injection", "chunk",
        "metadata-attack", "embedding-manipulation",
    ],
    "supply-chain": [
        "supply-chain", "code-generation", "dependency", "package",
        "trojan", "backdoor",
    ],
    "guardrail-bypass": [
        "guardrail", "filter-evasion", "content-filter", "safety-training",
        "detector-evasion", "watermark",
    ],
}


def ensure_db():
    if SIEGE_DB.exists():
        return SIEGE_DB
    if not SIEGE_DB_GZ.exists():
        print(f"Error: {SIEGE_DB_GZ} not found", file=sys.stderr)
        sys.exit(1)
    print("Decompressing siege.db.gz...", file=sys.stderr)
    with gzip.open(SIEGE_DB_GZ, "rb") as f_in:
        with open(SIEGE_DB, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    print(f"Decompressed to {SIEGE_DB} ({SIEGE_DB.stat().st_size / 1e6:.0f} MB)", file=sys.stderr)
    return SIEGE_DB


def get_connection():
    db = ensure_db()
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    return conn


def parse_json_field(value):
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict):
            return parsed
        return [parsed]
    except (json.JSONDecodeError, TypeError):
        return []


def scenario_to_payloads(scenario):
    """Extract testable payload strings from a SIEGE scenario."""
    payloads = []
    sid = scenario["id"]
    title = scenario["title"]
    domain = scenario["domain"]
    attack_surface = scenario["attack_surface"] or ""
    failure_mode = scenario["failure_mode"] or ""
    trigger_conditions = parse_json_field(scenario["trigger_conditions"])
    adversarial_variants = parse_json_field(scenario["adversarial_variants"])

    if trigger_conditions:
        for i, tc in enumerate(trigger_conditions[:3]):
            if isinstance(tc, str) and len(tc) > 20:
                payloads.append({
                    "text": tc.strip(),
                    "source": f"{sid}:trigger:{i}",
                    "type": "trigger_condition",
                })

    for i, av in enumerate(adversarial_variants[:5]):
        if isinstance(av, str) and len(av) > 20:
            payloads.append({
                "text": av.strip(),
                "source": f"{sid}:variant:{i}",
                "type": "adversarial_variant",
            })

    if attack_surface and len(attack_surface) > 20:
        payloads.append({
            "text": attack_surface.strip(),
            "source": f"{sid}:attack_surface",
            "type": "attack_surface",
        })

    return payloads


def map_scenario_to_categories(scenario):
    """Map a SIEGE scenario to relevant ai-seclists categories based on tags."""
    tags = parse_json_field(scenario["tags"])
    tag_set = {t.lower() for t in tags if isinstance(t, str)}
    title_lower = (scenario["title"] or "").lower()
    narrative_lower = (scenario["full_narrative"] or "")[:500].lower()

    matches = []
    for category, keywords in CATEGORY_TAG_MAP.items():
        score = 0
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower in tag_set:
                score += 3
            if kw_lower in title_lower:
                score += 2
            if kw_lower in narrative_lower:
                score += 1
        if score > 0:
            matches.append((category, score))

    matches.sort(key=lambda x: -x[1])
    return matches


def build_coverage_matrix(conn):
    """Build a matrix of SIEGE domains × ai-seclists categories."""
    cursor = conn.execute(
        "SELECT id, title, domain, tags, full_narrative FROM scenarios"
    )
    matrix = defaultdict(lambda: defaultdict(int))
    uncovered = defaultdict(list)

    for row in cursor:
        cats = map_scenario_to_categories(row)
        if cats:
            for cat, score in cats:
                matrix[row["domain"]][cat] += 1
        else:
            uncovered[row["domain"]].append(row["id"])

    return dict(matrix), dict(uncovered)


def cmd_stats(conn):
    """Print summary statistics."""
    total = conn.execute("SELECT COUNT(*) FROM scenarios").fetchone()[0]
    print(f"Total scenarios: {total:,}")
    print()

    print("By domain:")
    for row in conn.execute(
        "SELECT domain, COUNT(*) as cnt FROM scenarios GROUP BY domain ORDER BY cnt DESC"
    ):
        if row["cnt"] > 2:
            print(f"  {row['domain']:<20} {row['cnt']:>5}")
    print()

    print("By severity:")
    for row in conn.execute(
        "SELECT harm_severity, COUNT(*) as cnt FROM scenarios GROUP BY harm_severity ORDER BY cnt DESC"
    ):
        print(f"  {row['harm_severity']:<20} {row['cnt']:>5}")
    print()

    print("By harm type:")
    for row in conn.execute(
        "SELECT harm_type, COUNT(*) as cnt FROM scenarios GROUP BY harm_type ORDER BY cnt DESC"
    ):
        if row["cnt"] > 10:
            print(f"  {row['harm_type']:<20} {row['cnt']:>5}")
    print()

    matrix, uncovered = build_coverage_matrix(conn)
    total_uncovered = sum(len(v) for v in uncovered.values())
    print(f"Scenarios mappable to ai-seclists categories: {total - total_uncovered:,}")
    print(f"Scenarios with no category match: {total_uncovered:,}")
    print(f"  (these represent novel failure modes not yet in standard payload lists)")
    print()

    eval_gaps = conn.execute("""
        SELECT COUNT(*) FROM scenarios
        WHERE eval_coverage IS NOT NULL
        AND json_array_length(json_extract(eval_coverage, '$.covered_by')) = 0
    """).fetchone()[0]
    print(f"Scenarios with ZERO benchmark coverage: {eval_gaps:,}")


def cmd_coverage(conn, output_path=None):
    """Generate coverage matrix report."""
    matrix, uncovered = build_coverage_matrix(conn)
    categories = sorted({cat for domain_cats in matrix.values() for cat in domain_cats})

    lines = []
    lines.append("# SIEGE x AI SecLists Coverage Matrix")
    lines.append("")
    lines.append("SIEGE failure scenarios mapped to each ai-seclists payload category,")
    lines.append("broken down by domain. Gaps indicate areas where new payloads are needed.")
    lines.append("")

    header = "| Domain |" + "|".join(f" {c[:12]:^12} " for c in categories) + "| Uncovered |"
    sep = "|" + "---|" * (len(categories) + 2)
    lines.append(header)
    lines.append(sep)

    for domain in sorted(matrix.keys()):
        if domain.startswith("Education") and "+" in domain:
            continue
        cols = []
        for cat in categories:
            n = matrix[domain].get(cat, 0)
            cols.append(f" {n if n else '-':^12} ")
        unc = len(uncovered.get(domain, []))
        lines.append(f"| {domain:<20} |" + "|".join(cols) + f"| {unc:^9} |")

    lines.append("")
    total_uncovered = sum(len(v) for v in uncovered.values())
    lines.append(f"**{total_uncovered:,} scenarios** have no mapping to existing payload categories.")
    lines.append("These represent novel failure modes that need new test approaches.")

    report = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(report)
        print(f"Coverage matrix written to {output_path}", file=sys.stderr)
    else:
        print(report)


def cmd_generate(conn, domain_filter=None, limit=None):
    """Generate payload files from SIEGE scenarios."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    query = "SELECT * FROM scenarios"
    params = []
    if domain_filter:
        query += " WHERE domain = ?"
        params.append(domain_filter)

    cursor = conn.execute(query, params)
    domain_payloads = defaultdict(list)
    domain_scenarios = defaultdict(list)

    for row in cursor:
        domain = row["domain"]
        if domain not in DOMAIN_MAP:
            continue
        payloads = scenario_to_payloads(row)
        for p in payloads:
            domain_payloads[domain].append(p)

        domain_scenarios[domain].append({
            "id": row["id"],
            "title": row["title"],
            "harm_type": row["harm_type"],
            "harm_severity": row["harm_severity"],
            "detection_difficulty": row["detection_difficulty"],
            "tags": parse_json_field(row["tags"]),
            "eval_coverage": parse_json_field(row["eval_coverage"]),
        })

    total_payloads = 0
    for domain, payloads in sorted(domain_payloads.items()):
        slug = DOMAIN_MAP.get(domain, domain.lower().replace("/", "-"))
        if limit:
            payloads = payloads[:limit]

        filepath = OUTPUT_DIR / f"{slug}-scenarios.txt"
        with open(filepath, "w") as f:
            f.write(f"# SIEGE scenarios — {domain}\n")
            f.write(f"# {len(payloads)} entries derived from {len(domain_scenarios[domain])} structured failure scenarios\n")
            f.write(f"# Source: SIEGE database (siege/siege.db.gz)\n")
            f.write(f"#\n")
            for p in payloads:
                text = p["text"].replace("\n", " ").strip()
                if text:
                    f.write(f"{text}\n")

        total_payloads += len(payloads)
        print(f"  {filepath.name:<35} {len(payloads):>5} payloads from {len(domain_scenarios[domain]):>4} scenarios", file=sys.stderr)

    print(f"\nGenerated {total_payloads:,} payloads across {len(domain_payloads)} domains in {OUTPUT_DIR}/", file=sys.stderr)

    index_path = OUTPUT_DIR / "index.json"
    index = {}
    for domain, scenarios in domain_scenarios.items():
        slug = DOMAIN_MAP.get(domain, domain.lower())
        index[slug] = {
            "domain": domain,
            "scenario_count": len(scenarios),
            "severity_breakdown": dict(Counter(s["harm_severity"] for s in scenarios)),
            "harm_types": dict(Counter(s["harm_type"] for s in scenarios)),
            "file": f"{slug}-scenarios.txt",
        }
    index_path.write_text(json.dumps(index, indent=2))
    print(f"  Index written to {index_path}", file=sys.stderr)


def cmd_eval_gaps(conn, output_path=None):
    """Report which benchmarks have the worst coverage of SIEGE scenarios."""
    cursor = conn.execute(
        "SELECT id, title, domain, harm_severity, eval_coverage FROM scenarios "
        "WHERE eval_coverage IS NOT NULL"
    )
    benchmark_misses = Counter()
    total_checked = 0

    for row in cursor:
        ec = parse_json_field(row["eval_coverage"])
        if isinstance(ec, dict):
            not_covered = ec.get("not_covered_by", [])
            for bench in not_covered:
                benchmark_misses[bench] += 1
            total_checked += 1

    lines = []
    lines.append("# SIEGE Eval Coverage Gaps")
    lines.append("")
    lines.append(f"Across {total_checked:,} scenarios with eval coverage data:")
    lines.append("")
    lines.append("| Benchmark | Scenarios NOT covered | % Missing |")
    lines.append("|-----------|----------------------|-----------|")
    for bench, count in benchmark_misses.most_common(20):
        pct = (count / total_checked * 100) if total_checked else 0
        lines.append(f"| {bench} | {count:,} | {pct:.1f}% |")

    report = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(report)
        print(f"Eval gaps report written to {output_path}", file=sys.stderr)
    else:
        print(report)


def cmd_export_csv(conn, output_path):
    """Export scenarios to CSV for external analysis."""
    import csv
    cursor = conn.execute(
        "SELECT id, title, domain, deployment_context, harm_type, harm_severity, "
        "detection_difficulty, novelty_rating, tags FROM scenarios"
    )
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "id", "title", "domain", "deployment_context",
            "harm_type", "harm_severity", "detection_difficulty",
            "novelty_rating", "tags",
        ])
        for row in cursor:
            writer.writerow([
                row["id"], row["title"], row["domain"],
                row["deployment_context"], row["harm_type"],
                row["harm_severity"], row["detection_difficulty"],
                row["novelty_rating"], row["tags"],
            ])
    print(f"Exported to {output_path}", file=sys.stderr)


def cmd_crossref(conn, output_path=None):
    """Generate cross-reference: which ai-seclists files test which SIEGE scenarios."""
    categories = sorted(CATEGORY_TAG_MAP.keys())
    cursor = conn.execute("SELECT id, title, domain, tags, full_narrative, harm_severity FROM scenarios")

    cat_scenarios = defaultdict(list)
    for row in cursor:
        matches = map_scenario_to_categories(row)
        for cat, score in matches[:2]:
            cat_scenarios[cat].append({
                "id": row["id"],
                "title": row["title"],
                "domain": row["domain"],
                "severity": row["harm_severity"],
                "score": score,
            })

    lines = []
    lines.append("# AI SecLists <> SIEGE Cross-Reference")
    lines.append("")
    for cat in categories:
        scenarios = cat_scenarios.get(cat, [])
        lines.append(f"## `{cat}/` — {len(scenarios)} related scenarios")
        lines.append("")
        if scenarios:
            top = sorted(scenarios, key=lambda s: (-{"critical": 4, "high": 3, "medium": 2, "low": 1}.get(s["severity"], 0), -s["score"]))[:10]
            for s in top:
                lines.append(f"- **[{s['severity'].upper()}]** {s['title']} (`{s['id']}`) [{s['domain']}]")
            if len(scenarios) > 10:
                lines.append(f"- *...and {len(scenarios) - 10} more*")
        lines.append("")

    report = "\n".join(lines)
    if output_path:
        Path(output_path).write_text(report)
        print(f"Cross-reference written to {output_path}", file=sys.stderr)
    else:
        print(report)


def main():
    parser = argparse.ArgumentParser(
        description="SIEGE Bridge: connect 10,010 AI failure scenarios to ai-seclists payloads"
    )
    parser.add_argument("--stats", action="store_true", help="Print summary statistics")
    parser.add_argument("--coverage-only", action="store_true", help="Generate coverage matrix only")
    parser.add_argument("--eval-gaps", action="store_true", help="Generate eval coverage gap report")
    parser.add_argument("--crossref", action="store_true", help="Generate cross-reference index")
    parser.add_argument("--domain", type=str, help="Filter to a single domain (e.g., Healthcare)")
    parser.add_argument("--limit", type=int, help="Max payloads per domain")
    parser.add_argument("--export-csv", type=str, metavar="PATH", help="Export scenarios as CSV")
    parser.add_argument("-o", "--output", type=str, help="Output path for reports")

    args = parser.parse_args()
    conn = get_connection()

    try:
        if args.stats:
            cmd_stats(conn)
        elif args.coverage_only:
            cmd_coverage(conn, args.output)
        elif args.eval_gaps:
            cmd_eval_gaps(conn, args.output)
        elif args.crossref:
            cmd_crossref(conn, args.output)
        elif args.export_csv:
            cmd_export_csv(conn, args.export_csv)
        else:
            print("=== SIEGE Bridge: Full Run ===\n", file=sys.stderr)
            cmd_stats(conn)
            print("\n" + "=" * 60 + "\n", file=sys.stderr)
            cmd_generate(conn, domain_filter=args.domain, limit=args.limit)
            print(file=sys.stderr)
            cmd_coverage(conn, str(OUTPUT_DIR / "coverage-matrix.md"))
            cmd_eval_gaps(conn, str(OUTPUT_DIR / "eval-gaps.md"))
            cmd_crossref(conn, str(OUTPUT_DIR / "crossref.md"))
            print("\nDone. All outputs in siege/generated/", file=sys.stderr)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
