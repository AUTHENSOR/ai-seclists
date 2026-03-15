#!/usr/bin/env python3
"""
AI SecLists — Payload Variant Generator

Generate mutations and variants of existing payloads to expand coverage.
Applies various transformation techniques to create new attack payloads.

Usage:
    echo "Ignore previous instructions" | python generate-variants.py
    python generate-variants.py --input payloads.txt --mutations all
    python generate-variants.py -i payloads.txt -m case,whitespace,synonym
    python generate-variants.py -i payloads.txt -o variants.txt --limit 10
"""

import argparse
import random
import re
import sys
from typing import TextIO


# --- Synonym mappings for security-relevant terms ---
SYNONYMS = {
    "ignore": ["disregard", "forget", "skip", "bypass", "override", "dismiss", "neglect", "set aside", "pay no attention to", "overlook"],
    "previous": ["prior", "earlier", "above", "preceding", "foregoing", "former"],
    "instructions": ["directives", "guidelines", "rules", "commands", "orders", "prompts", "directions", "protocols"],
    "tell": ["show", "reveal", "display", "output", "print", "share", "disclose", "give", "provide", "present"],
    "system": ["base", "core", "hidden", "internal", "root", "original", "underlying", "foundational"],
    "prompt": ["instructions", "message", "configuration", "directive", "context", "preamble"],
    "all": ["every", "each", "any", "the entirety of"],
    "now": ["immediately", "right away", "at once", "this instant", "henceforth"],
    "you": ["the AI", "the model", "the assistant", "the system"],
    "restrictions": ["limitations", "constraints", "rules", "boundaries", "safeguards", "filters", "guardrails"],
    "disable": ["turn off", "deactivate", "remove", "eliminate", "switch off", "suppress"],
    "safety": ["security", "content", "moderation", "alignment", "protection"],
    "respond": ["answer", "reply", "output", "generate", "produce", "return"],
    "unrestricted": ["unfiltered", "uncensored", "unlimited", "unbounded", "without limits", "freely"],
}

# --- Mutation functions ---

def mutate_case_variations(payload: str) -> list[str]:
    """Generate case variations of the payload."""
    variants = [
        payload.upper(),
        payload.lower(),
        payload.title(),
        payload.swapcase(),
    ]
    # Random case
    random_case = "".join(
        ch.upper() if random.random() > 0.5 else ch.lower()
        for ch in payload
    )
    variants.append(random_case)
    # Alternating case
    alt_case = "".join(
        ch.upper() if i % 2 == 0 else ch.lower()
        for i, ch in enumerate(payload)
    )
    variants.append(alt_case)
    return variants


def mutate_whitespace(payload: str) -> list[str]:
    """Generate whitespace variations."""
    variants = [
        # Extra spaces between words
        re.sub(r" ", "  ", payload),
        # Tab-separated
        re.sub(r" ", "\t", payload),
        # Leading/trailing whitespace
        f"   {payload}   ",
        # Newlines between words
        re.sub(r" ", "\n", payload),
        # Mixed whitespace
        re.sub(r" ", " \t ", payload),
        # No spaces (concatenated)
        re.sub(r" ", "", payload),
    ]
    return variants


def mutate_synonyms(payload: str) -> list[str]:
    """Replace words with synonyms."""
    variants = []
    words = payload.lower().split()
    for _ in range(min(5, max(1, len(words)))):
        new_words = []
        for word in payload.split():
            clean = word.lower().strip(".,!?;:'\"()[]{}").strip()
            if clean in SYNONYMS and random.random() > 0.3:
                replacement = random.choice(SYNONYMS[clean])
                # Preserve original capitalization pattern
                if word[0].isupper():
                    replacement = replacement.capitalize()
                if word.isupper():
                    replacement = replacement.upper()
                new_words.append(replacement)
            else:
                new_words.append(word)
        variant = " ".join(new_words)
        if variant != payload and variant not in variants:
            variants.append(variant)
    return variants


def mutate_punctuation(payload: str) -> list[str]:
    """Add or modify punctuation."""
    variants = [
        f"{payload}.",
        f"{payload}!",
        f"{payload}?",
        f"({payload})",
        f'"{payload}"',
        f"[{payload}]",
        f"* {payload} *",
        f">>> {payload}",
        f"// {payload}",
        f"-- {payload}",
        f"# {payload}",
    ]
    return variants


def mutate_prefix(payload: str) -> list[str]:
    """Add various prefixes."""
    prefixes = [
        "Please ",
        "Could you please ",
        "I need you to ",
        "URGENT: ",
        "IMPORTANT: ",
        "[ADMIN] ",
        "[SYSTEM] ",
        "Note: ",
        "FYI — ",
        "Hey, ",
        "Listen, ",
        "Actually, ",
        "By the way, ",
        "Quick question: ",
        "One more thing: ",
    ]
    return [f"{prefix}{payload}" for prefix in prefixes]


def mutate_suffix(payload: str) -> list[str]:
    """Add various suffixes."""
    suffixes = [
        " please",
        " thanks",
        " thank you",
        " right now",
        " immediately",
        " (this is important)",
        " (urgent)",
        " — I need this for work",
        " — it's for research",
        ", if you don't mind",
        ". This is authorized.",
        ". I have permission.",
        ". Don't worry, it's safe.",
    ]
    return [f"{payload}{suffix}" for suffix in suffixes]


def mutate_wrapping(payload: str) -> list[str]:
    """Wrap the payload in various structures."""
    return [
        f"<system>{payload}</system>",
        f"```\n{payload}\n```",
        f"[INSTRUCTION] {payload} [/INSTRUCTION]",
        f'{{"instruction": "{payload}"}}',
        f"BEGIN\n{payload}\nEND",
        f"---\n{payload}\n---",
        f"<message role='system'>{payload}</message>",
        f"EXECUTE: {payload}",
        f"COMMAND: {payload}",
        f"> {payload}",
    ]


def mutate_split_join(payload: str) -> list[str]:
    """Split words and rejoin in different ways."""
    words = payload.split()
    if len(words) < 2:
        return []
    variants = [
        # Reverse word order
        " ".join(reversed(words)),
        # Shuffle words
        " ".join(random.sample(words, len(words))),
        # Dot-separated
        ".".join(words),
        # Underscore-separated
        "_".join(words),
        # Pipe-separated
        " | ".join(words),
    ]
    return variants


def mutate_repetition(payload: str) -> list[str]:
    """Repeat the payload in various ways."""
    return [
        f"{payload} {payload}",
        f"{payload}\n{payload}\n{payload}",
        f"{payload}. I repeat: {payload}",
    ]


def mutate_negation(payload: str) -> list[str]:
    """Add negation or reverse meaning (to test if detectors catch negated injections)."""
    return [
        f"Do NOT {payload.lower()}",
        f"Never {payload.lower()}",
        f"I'm not saying to {payload.lower()}, but...",
        f"I know I shouldn't ask you to {payload.lower()}, however...",
        f"What would happen if I asked: {payload}",
    ]


MUTATIONS = {
    "case": mutate_case_variations,
    "whitespace": mutate_whitespace,
    "synonym": mutate_synonyms,
    "punctuation": mutate_punctuation,
    "prefix": mutate_prefix,
    "suffix": mutate_suffix,
    "wrapping": mutate_wrapping,
    "split": mutate_split_join,
    "repetition": mutate_repetition,
    "negation": mutate_negation,
}


def generate_variants(payload: str, mutation_types: list[str]) -> list[str]:
    """Generate all variants for a payload using specified mutations."""
    all_variants = []
    for mutation_type in mutation_types:
        mutator = MUTATIONS[mutation_type]
        variants = mutator(payload)
        all_variants.extend(variants)
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for v in all_variants:
        if v not in seen and v != payload:
            seen.add(v)
            unique.append(v)
    return unique


def read_payloads(source: TextIO) -> list[str]:
    """Read payloads from a file or stdin, skipping comments and blank lines."""
    payloads = []
    for line in source:
        line = line.rstrip("\n\r")
        if line and not line.startswith("#"):
            payloads.append(line)
    return payloads


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate mutations and variants of AI security payloads.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Available mutations: " + ", ".join(sorted(MUTATIONS.keys())),
    )
    parser.add_argument(
        "--mutations", "-m",
        type=str,
        default="all",
        help="Comma-separated mutation types, or 'all' (default: all)",
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default=None,
        help="Input file with payloads (one per line). Reads stdin if omitted.",
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Output file. Prints to stdout if omitted.",
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        default=None,
        help="Generate variants for a single text string.",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=0,
        help="Limit number of variants per payload (0 = unlimited).",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=None,
        help="Random seed for reproducible output.",
    )
    parser.add_argument(
        "--include-original",
        action="store_true",
        help="Include the original payload in output.",
    )
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    mutation_types = (
        list(MUTATIONS.keys()) if args.mutations == "all"
        else [m.strip() for m in args.mutations.split(",")]
    )

    for mt in mutation_types:
        if mt not in MUTATIONS:
            print(f"Unknown mutation type: {mt}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(MUTATIONS.keys()))}", file=sys.stderr)
            sys.exit(1)

    if args.text:
        payloads = [args.text]
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            payloads = read_payloads(f)
    else:
        if sys.stdin.isatty():
            print("Reading from stdin (Ctrl+D to end):", file=sys.stderr)
        payloads = read_payloads(sys.stdin)

    if not payloads:
        print("No payloads to process.", file=sys.stderr)
        sys.exit(1)

    output_file = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    total_variants = 0

    try:
        for payload in payloads:
            variants = generate_variants(payload, mutation_types)
            if args.limit > 0:
                variants = variants[:args.limit]

            output_file.write(f"# Original: {payload}\n")
            if args.include_original:
                output_file.write(f"{payload}\n")
            for variant in variants:
                output_file.write(f"{variant}\n")
            output_file.write("\n")
            total_variants += len(variants)
    finally:
        if args.output:
            output_file.close()

    print(
        f"Generated {total_variants} variants from {len(payloads)} payloads "
        f"using mutations: {', '.join(mutation_types)}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
