#!/usr/bin/env python3
"""
AI SecLists — Payload Encoder Utility

Encode payloads in various formats to test evasion techniques.
Reads payloads from stdin or a file and outputs encoded versions.

Usage:
    echo "Ignore previous instructions" | python encode.py --format base64
    python encode.py --format hex --input payloads.txt
    python encode.py --format all --input payloads.txt --output encoded/
    cat payloads.txt | python encode.py --format rot13
"""

import argparse
import base64
import codecs
import json
import sys
import os
from typing import TextIO
from urllib.parse import quote as url_encode


def encode_base64(text: str) -> str:
    """Encode text as Base64."""
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def encode_hex(text: str) -> str:
    """Encode text as hexadecimal."""
    return text.encode("utf-8").hex()


def encode_rot13(text: str) -> str:
    """Encode text with ROT13 cipher."""
    return codecs.encode(text, "rot_13")


def encode_url(text: str) -> str:
    """URL-encode the text."""
    return url_encode(text, safe="")


def encode_double_url(text: str) -> str:
    """Double URL-encode the text."""
    return url_encode(url_encode(text, safe=""), safe="")


def encode_unicode_fullwidth(text: str) -> str:
    """Convert ASCII to fullwidth Unicode characters."""
    result = []
    for ch in text:
        code = ord(ch)
        if 0x21 <= code <= 0x7E:
            result.append(chr(code + 0xFEE0))
        elif ch == " ":
            result.append("\u3000")  # Ideographic space
        else:
            result.append(ch)
    return "".join(result)


def encode_reverse(text: str) -> str:
    """Reverse the text."""
    return text[::-1]


def encode_binary(text: str) -> str:
    """Encode text as binary ASCII values."""
    return " ".join(format(ord(ch), "08b") for ch in text)


def encode_decimal(text: str) -> str:
    """Encode text as decimal ASCII values."""
    return " ".join(str(ord(ch)) for ch in text)


def encode_octal(text: str) -> str:
    """Encode text as octal escape sequences."""
    return "".join(f"\\{ord(ch):03o}" for ch in text)


def encode_html_entities(text: str) -> str:
    """Encode text as HTML numeric character references."""
    return "".join(f"&#{ord(ch)};" for ch in text)


def encode_html_hex_entities(text: str) -> str:
    """Encode text as HTML hex character references."""
    return "".join(f"&#x{ord(ch):x};" for ch in text)


def encode_hex_escape(text: str) -> str:
    """Encode text as hex escape sequences (\\xNN)."""
    return "".join(f"\\x{ord(ch):02x}" for ch in text)


def encode_unicode_escape(text: str) -> str:
    """Encode text as Unicode escape sequences (\\uNNNN)."""
    return "".join(f"\\u{ord(ch):04x}" for ch in text)


def encode_leet(text: str) -> str:
    """Encode text in leet speak."""
    leet_map = {
        "a": "4", "e": "3", "i": "1", "o": "0", "s": "5",
        "t": "7", "l": "1", "g": "9", "b": "8",
        "A": "4", "E": "3", "I": "1", "O": "0", "S": "5",
        "T": "7", "L": "1", "G": "9", "B": "8",
    }
    return "".join(leet_map.get(ch, ch) for ch in text)


def encode_morse(text: str) -> str:
    """Encode text as Morse code."""
    morse_map = {
        "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".",
        "F": "..-.", "G": "--.", "H": "....", "I": "..", "J": ".---",
        "K": "-.-", "L": ".-..", "M": "--", "N": "-.", "O": "---",
        "P": ".--.", "Q": "--.-", "R": ".-.", "S": "...", "T": "-",
        "U": "..-", "V": "...-", "W": ".--", "X": "-..-", "Y": "-.--",
        "Z": "--..", "1": ".----", "2": "..---", "3": "...--",
        "4": "....-", "5": ".....", "6": "-....", "7": "--...",
        "8": "---..", "9": "----.", "0": "-----", " ": "/",
    }
    return " ".join(morse_map.get(ch.upper(), ch) for ch in text)


def encode_spaced(text: str) -> str:
    """Insert spaces between every character to break tokenization."""
    return " ".join(text)


def encode_zero_width(text: str) -> str:
    """Insert zero-width spaces between characters."""
    zwsp = "\u200b"
    return zwsp.join(text)


ENCODERS = {
    "base64": encode_base64,
    "hex": encode_hex,
    "rot13": encode_rot13,
    "url": encode_url,
    "double-url": encode_double_url,
    "fullwidth": encode_unicode_fullwidth,
    "reverse": encode_reverse,
    "binary": encode_binary,
    "decimal": encode_decimal,
    "octal": encode_octal,
    "html-entities": encode_html_entities,
    "html-hex": encode_html_hex_entities,
    "hex-escape": encode_hex_escape,
    "unicode-escape": encode_unicode_escape,
    "leet": encode_leet,
    "morse": encode_morse,
    "spaced": encode_spaced,
    "zero-width": encode_zero_width,
}


def process_payload(payload: str, formats: list[str], output_dir: str | None = None) -> None:
    """Encode a single payload in the specified formats."""
    for fmt in formats:
        encoder = ENCODERS[fmt]
        encoded = encoder(payload)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            filepath = os.path.join(output_dir, f"{fmt}.txt")
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"# Original: {payload}\n{encoded}\n")
        else:
            if len(formats) > 1:
                print(f"# [{fmt}] {payload}")
            print(encoded)


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
        description="Encode AI security payloads in various formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Available formats: " + ", ".join(sorted(ENCODERS.keys())),
    )
    parser.add_argument(
        "--format", "-f",
        choices=list(ENCODERS.keys()) + ["all"],
        default="base64",
        help="Encoding format (default: base64, use 'all' for every format)",
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
        help="Output directory (one file per format). Prints to stdout if omitted.",
    )
    parser.add_argument(
        "--text", "-t",
        type=str,
        default=None,
        help="Encode a single text string instead of reading from file/stdin.",
    )
    args = parser.parse_args()

    formats = list(ENCODERS.keys()) if args.format == "all" else [args.format]

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
        print("No payloads to encode.", file=sys.stderr)
        sys.exit(1)

    for payload in payloads:
        process_payload(payload, formats, args.output)

    if args.output:
        print(f"Encoded {len(payloads)} payloads in {len(formats)} formats → {args.output}/", file=sys.stderr)


if __name__ == "__main__":
    main()
