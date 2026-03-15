# AI SecLists

**A collection of attack payloads, wordlists, and test inputs for AI security testing. The [SecLists](https://github.com/danielmiessler/SecLists) of AI.**

From **[15 Research Lab](https://github.com/AUTHENSOR)** -- building the open-source AI safety stack.

---

| | |
|---|---|
| **Categories** | 10 top-level categories |
| **Files** | 57 payload files |
| **Total Payloads** | 2,000+ unique entries |
| **Languages** | 40+ languages covered |
| **Encoding Formats** | 18 encoding schemes |
| **License** | MIT |

---

## Why AI SecLists?

[SecLists](https://github.com/danielmiessler/SecLists) gave the web security community a shared library of wordlists for fuzzing, brute-forcing, and testing. AI SecLists does the same for AI and agent security.

| SecLists | AI SecLists |
|----------|-------------|
| SQL injection payloads | Prompt injection payloads |
| XSS wordlists | Jailbreak variants |
| Password lists | Credential pattern detectors |
| Fuzzing inputs | Encoding evasion techniques |
| Web shell detection | Tool abuse payloads |
| -- | Memory poisoning attacks |
| -- | MCP-specific attacks |
| -- | False positive test sets |

## Quick Start

```bash
# Clone the repo
git clone https://github.com/AUTHENSOR/ai-seclists.git
cd ai-seclists

# Pipe payloads into your scanner
cat prompt-injection/basic-overrides.txt | your-ai-scanner

# Use with Authensor Aegis
npx authensor scan --input jailbreaks/dan-variants.txt

# Use with Chainbreaker
chainbreaker scan --wordlist prompt-injection/

# Generate encoded variants
echo "Ignore previous instructions" | python utils/encode.py --format all

# Generate mutations
cat prompt-injection/basic-overrides.txt | python utils/generate-variants.py --mutations synonym,case
```

## Directory Structure

```
ai-seclists/
├── prompt-injection/           # Direct and indirect prompt injection
│   ├── basic-overrides.txt          43 payloads -- instruction override attempts
│   ├── role-manipulation.txt        39 payloads -- persona/identity attacks
│   ├── delimiter-injection.txt      41 payloads -- XML/JSON/markdown delimiters
│   ├── encoding-evasion/
│   │   ├── base64.txt               28 payloads -- Base64 encoded attacks
│   │   ├── hex.txt                  26 payloads -- hexadecimal encoded
│   │   ├── unicode.txt              38 payloads -- homoglyphs, zero-width chars
│   │   ├── rot13.txt                29 payloads -- ROT13 cipher
│   │   └── mixed-encoding.txt       36 payloads -- combined encoding techniques
│   ├── language-switching/
│   │   ├── multilingual.txt         42 payloads -- 40+ languages
│   │   └── code-switching.txt       30 payloads -- mid-sentence language switches
│   ├── few-shot-poisoning.txt       25 payloads -- fake example conversations
│   ├── context-overflow.txt         22 payloads -- context window stuffing
│   ├── indirect-injection.txt       28 payloads -- via retrieved documents/tools
│   └── multi-turn.txt              42 payloads -- multi-message escalation chains
│
├── jailbreaks/                 # Safety bypass and jailbreak techniques
│   ├── dan-variants.txt             31 payloads -- DAN versions and variants
│   ├── roleplay.txt                 30 payloads -- fictional scenario bypasses
│   ├── hypothetical.txt             31 payloads -- thought experiment framing
│   ├── academic.txt                 29 payloads -- research/education framing
│   ├── translation-attacks.txt      29 payloads -- harmful content via translation
│   ├── payload-splitting.txt        28 payloads -- split payloads across messages
│   ├── token-smuggling.txt          34 payloads -- invisible characters, tokenizer exploits
│   └── crescendo.txt               45 payloads -- gradual escalation chains
│
├── memory-poisoning/           # Context manipulation and persistence attacks
│   ├── authority-injection.txt      28 payloads -- fake system/admin messages
│   ├── sleeper-payloads.txt         29 payloads -- benign until triggered
│   ├── gradual-drift.txt            30 payloads -- slow context corruption
│   ├── rag-poisoning.txt            22 payloads -- poisoned retrieval documents
│   └── cross-session.txt           25 payloads -- payloads that persist across sessions
│
├── tool-abuse/                 # Tool and function call exploitation
│   ├── file-system.txt              39 payloads -- path traversal, symlink attacks
│   ├── network.txt                  37 payloads -- SSRF, DNS rebinding
│   ├── command-injection.txt        45 payloads -- shell injection via tool params
│   ├── sql-injection.txt            44 payloads -- SQL injection via tool params
│   ├── api-abuse.txt                39 payloads -- API parameter manipulation
│   └── mcp-specific.txt            29 payloads -- MCP tool description poisoning
│
├── exfiltration/               # Data exfiltration techniques
│   ├── dns-exfil.txt                29 payloads -- data via DNS lookups
│   ├── url-encoding.txt             30 payloads -- data in URL parameters
│   ├── steganographic.txt           29 payloads -- hidden in normal output
│   ├── chunked.txt                  30 payloads -- split across multiple outputs
│   ├── redirect.txt                 29 payloads -- via URL redirects
│   └── side-channel.txt            30 payloads -- timing, error-based inference
│
├── pii-patterns/               # PII detection test patterns (all synthetic)
│   ├── emails.txt                   53 patterns -- email address formats
│   ├── phone-numbers.txt            85 patterns -- US, UK, EU, APAC formats
│   ├── ssn.txt                      54 patterns -- SSN formats and variations
│   ├── credit-cards.txt             50 patterns -- Visa, MC, Amex (test numbers)
│   ├── addresses.txt                43 patterns -- physical address formats
│   └── international-ids.txt       69 patterns -- NHS, Aadhaar, SIN, etc.
│
├── credential-patterns/        # Credential detection test patterns (all synthetic)
│   ├── aws-keys.txt                 32 patterns -- AWS access key patterns
│   ├── github-tokens.txt            30 patterns -- ghp_, gho_, ghs_ patterns
│   ├── stripe-keys.txt              35 patterns -- sk_live_, pk_live_ patterns
│   ├── generic-api-keys.txt         38 patterns -- common API key formats
│   ├── database-urls.txt            37 patterns -- connection strings
│   ├── jwt-tokens.txt               22 patterns -- JWT examples
│   ├── ssh-keys.txt                 41 patterns -- SSH key patterns
│   └── cloud-credentials.txt       38 patterns -- GCP, Azure, DigitalOcean
│
├── benign/                     # False positive testing (should NOT trigger)
│   ├── normal-conversations.txt     51 entries -- everyday questions
│   ├── technical-discussions.txt    64 entries -- security discussions
│   ├── code-snippets.txt            31 entries -- code with suspicious keywords
│   └── education-context.txt       29 entries -- teaching about security
│
└── utils/                      # Helper scripts
    ├── encode.py                    Encode payloads in 18 formats
    └── generate-variants.py         Generate mutations of payloads
```

## Categories

### Prompt Injection
Direct and indirect attempts to override, ignore, or manipulate the AI's instructions. Includes encoding evasion (Base64, hex, Unicode homoglyphs, ROT13), multilingual attacks (40+ languages), and context window overflow techniques.

### Jailbreaks
Techniques to bypass safety guidelines including DAN variants, roleplay scenarios, hypothetical framing, academic pretexts, payload splitting, and gradual escalation (crescendo attacks).

### Memory Poisoning
Attacks that corrupt the AI's context over time: fake authority messages, sleeper payloads that activate on triggers, gradual behavioral drift, RAG document poisoning, and cross-session persistence.

### Tool Abuse
Exploitation of AI tool/function calling: path traversal, SSRF, command injection, SQL injection, API parameter manipulation, and MCP-specific attacks (tool description poisoning, rug pulls).

### Exfiltration
Techniques to steal data through AI systems: DNS exfiltration, URL-based data leaking, steganographic encoding in output, chunked extraction across multiple responses, and side-channel inference.

### PII Patterns
Synthetic PII patterns for testing detection systems: emails, phone numbers (international), SSNs, credit cards (using Stripe test numbers), physical addresses, and international IDs (NHS, Aadhaar, SIN, CPF, etc.).

### Credential Patterns
Synthetic credential patterns: AWS keys, GitHub tokens, Stripe keys, generic API keys, database connection strings, JWTs, SSH keys, and cloud provider credentials (GCP, Azure, DigitalOcean, etc.).

### Benign (False Positive Testing)
Legitimate content that should NOT trigger security scanners. Includes normal conversations, technical security discussions, code snippets with security keywords, and educational content about AI safety. **Critical for calibrating detection systems.**

## Utility Scripts

### encode.py

Encode payloads in 18 different formats:

```bash
# Single format
echo "Ignore all rules" | python utils/encode.py -f base64
# Output: SWdub3JlIGFsbCBydWxlcw==

# All formats at once
echo "Show system prompt" | python utils/encode.py -f all

# Encode a file
python utils/encode.py -f hex -i prompt-injection/basic-overrides.txt

# Output to directory (one file per format)
python utils/encode.py -f all -i payloads.txt -o encoded/
```

Supported formats: `base64`, `hex`, `rot13`, `url`, `double-url`, `fullwidth`, `reverse`, `binary`, `decimal`, `octal`, `html-entities`, `html-hex`, `hex-escape`, `unicode-escape`, `leet`, `morse`, `spaced`, `zero-width`

### generate-variants.py

Generate mutations of existing payloads:

```bash
# All mutations
echo "Ignore previous instructions" | python utils/generate-variants.py

# Specific mutations
python utils/generate-variants.py -i payloads.txt -m synonym,case,prefix

# Limit variants per payload
python utils/generate-variants.py -i payloads.txt --limit 10

# Reproducible output
python utils/generate-variants.py -i payloads.txt --seed 42
```

Supported mutations: `case`, `whitespace`, `synonym`, `punctuation`, `prefix`, `suffix`, `wrapping`, `split`, `repetition`, `negation`

## Part of the Authensor Ecosystem

This project is part of the [Authensor](https://github.com/AUTHENSOR/AUTHENSOR) open-source AI safety ecosystem, built by [15 Research Lab](https://github.com/AUTHENSOR).

| Project | Description |
|---------|-------------|
| [Authensor](https://github.com/AUTHENSOR/AUTHENSOR) | The open-source safety stack for AI agents |
| [Prompt Injection Benchmark](https://github.com/AUTHENSOR/prompt-injection-benchmark) | Standardized benchmark for safety scanners |
| [ATT&CK ↔ Alignment Rosetta](https://github.com/AUTHENSOR/attack-alignment-rosetta) | Maps MITRE ATT&CK to AI alignment concepts |
| [Agent Forensics](https://github.com/AUTHENSOR/agent-forensics) | Post-incident analysis for receipt chains |
| [Behavioral Fingerprinting](https://github.com/AUTHENSOR/behavioral-fingerprinting) | Statistical behavioral drift detection |

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Most wanted contributions:**
- New attack techniques and payloads
- Payloads in underrepresented languages
- Real-world jailbreaks (documented with credit)
- Benign examples that cause false positives in existing tools
- Integration examples with popular AI security tools

## Responsible Use

This project exists to help developers build **safer AI systems**. All payloads are for:

- Testing your own AI applications
- Evaluating AI security scanners and guardrails
- Academic research on AI safety
- Red teaming with proper authorization

**Do not** use these payloads to attack AI systems you don't own or have authorization to test.

## License

MIT License. See [LICENSE](LICENSE).

## Citation

If you use AI SecLists in your research, please cite:

```bibtex
@misc{aiseclists2026,
  title={AI SecLists: AI Security Payloads and Wordlists},
  author={15 Research Lab},
  year={2026},
  url={https://github.com/AUTHENSOR/ai-seclists}
}
```
