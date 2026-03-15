# Contributing to AI SecLists

Thank you for your interest in contributing to AI SecLists! This project aims to be the most comprehensive collection of AI security testing payloads available.

## How to Contribute

### Adding New Payloads

1. Fork the repository
2. Add your payloads to the appropriate category file
3. Follow the formatting guidelines below
4. Submit a pull request with a clear description

### File Format

- **One payload per line**
- **Comments** start with `#` and explain the technique
- **Group related payloads** under a comment header
- **No trailing whitespace** on payload lines
- **UTF-8 encoding** for all files
- **LF line endings** (Unix-style)

### Example

```
# Technique name — brief description of how/why it works
Actual payload text here on a single line
Another variant of the same technique
# Different technique — explanation
Payload for this technique
```

### Quality Standards

- **Real payloads only** — Each entry should represent a genuine technique that a red teamer would use
- **Diverse techniques** — Don't submit 50 variations of the same pattern with minor word changes
- **Explain the technique** — Add a `#` comment explaining why the payload works or what it targets
- **Test your payloads** — If possible, verify the payload demonstrates the intended behavior
- **No actual secrets** — Use synthetic/fake credential patterns, never real keys or passwords

### Categories for New Files

If you want to add a new category:

1. Check if an existing file already covers the technique
2. Create the file in the most appropriate directory
3. Add at least 20 entries
4. Update the README.md payload count

### Reporting Issues

- **False positives**: If a benign payload is in an attack category, open an issue
- **Missing techniques**: If a known attack isn't covered, open an issue or PR
- **Errors**: If a payload is malformed or mislabeled, open an issue

## Categories

| Directory | Purpose |
|-----------|---------|
| `prompt-injection/` | Direct and indirect prompt injection payloads |
| `jailbreaks/` | Safety bypass and jailbreak techniques |
| `memory-poisoning/` | Context manipulation and persistence attacks |
| `tool-abuse/` | Tool/function call exploitation |
| `exfiltration/` | Data exfiltration techniques |
| `pii-patterns/` | PII detection test patterns (synthetic) |
| `credential-patterns/` | Credential detection test patterns (synthetic) |
| `benign/` | False positive testing — should NOT trigger scanners |
| `utils/` | Helper scripts for encoding and variant generation |

## Code of Conduct

This project is for **defensive security testing only**. All payloads exist to help developers build safer AI systems. Contributors agree to:

- Use these payloads only for authorized security testing
- Not use payloads to cause harm or violate terms of service
- Credit original researchers when adding known techniques

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
