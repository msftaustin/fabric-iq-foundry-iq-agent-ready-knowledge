# Repository Agent Guidelines

## Purpose

This repository contains an internal Microsoft demo for employees to present Foundry IQ to
customers. The customer is the audience, not an operator of this repository. Keep presenter setup
clear, repeatable, and focused on the Azure+Fabric demo path.

## Safety and demo data

- Never commit credentials, tokens, tenant-specific endpoints, or generated `.env` files.
- Use synthetic Zava data and Microsoft-controlled demo identities only.
- Never use customer data, customer identities, or a personal employee mailbox in a demo.
- Work IQ is optional and requires approved synthetic content in the demo tenant.
- Do not change `LICENSE`, `LICENSE-DOCS`, `CODE_OF_CONDUCT.md`, or `SECURITY.md`.
- Do not add large slide decks, videos, or recordings. Link to approved hosted assets instead.
- Keep notebook outputs cleared and execution counts reset.
- Keep README files and the demo setup instructions synchronized with implementation.
- Do not modify GitHub workflow files without explicit permission.

## Demo content

- Keep the five notebook parts in order and preserve the Zava customer story where it explains
  the value of the feature being demonstrated.
- Write notebook openings as presenter demo flows, not attendee missions.
- End each notebook with a concise statement of the demo outcome.
- Use presenter prompts to help explain citations and source selection.
- Treat Parts 2, 4, and 5 as optional when their separate tenant capabilities are unavailable.
- Preserve customer-safe wording and do not promise production behavior from this demo.

## Contribution checks

Run the relevant repository tooling before submitting changes:

```bash
python scripts/demos.py validate
python -m unittest discover -s tests -v
```
