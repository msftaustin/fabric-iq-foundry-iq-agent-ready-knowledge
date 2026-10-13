# Contributing reusable demos

This repository uses a predictable demo package so presenters and technical teams can reuse a
scenario without first learning a custom folder layout.

## Create a demo

Run:

```bash
python scripts/demos.py new customer-scenario --title "Customer Scenario"
```

Demo identifiers use lowercase letters, numbers, and single dashes. The command creates
`demos/<id>/`, replaces its template tokens, and refreshes the catalog.

## Complete the package

| Location | Purpose |
|---|---|
| `demo.json` | Searchable metadata, readiness status, ownership, and entry points |
| `README.md` | Audience, value, architecture, prerequisites, and quickstart |
| `walkthrough/index.html` | Offline presentation story rendered by the shared player |
| `walkthrough/README.md` | Presenter preparation, narrative, and expected questions |
| `walkthrough/assets/` | Approved screenshots or diagrams used by the walkthrough |
| `src/` | Runnable implementation or an explicit source entry point |
| `infra/README.md` | Deployment options, configuration, security notes, and cleanup |
| `docs/EXTENDING.md` | Safe customization points and follow-on ideas |
| `tests/` | Optional automated tests owned by the demo |

The `status` field in `demo.json` must be `draft`, `ready`, or `deprecated`. Owners and deployment
targets must contain at least one value. All referenced entry points must stay inside the demo
package.

## Author a walkthrough

Define `window.WALKTHROUGH` before loading `shared/clickthrough/player.js`. Each step accepts a
title, HTML body, optional image and alt text, and optional presenter notes.

The player works when opened directly from disk. It supports the on-screen controls, arrow keys,
Home, End, and **N** for presenter notes. A `#step-N` URL fragment can open a specific step.

Only place trusted repository-authored HTML in a step body.

## Validate

Before opening a pull request, run:

```bash
python scripts/demos.py validate
python -m unittest discover -s tests -v
```

If validation reports a stale catalog, regenerate it with:

```bash
python scripts/demos.py catalog
```

## Repository rules

- Never commit credentials, tenant-specific values, or generated `.env` files.
- Link to recordings and slide decks instead of committing large binary assets.
- Reset notebook execution counts and clear outputs before committing notebooks.
- Keep dependencies pinned for runnable demo code.
- Document resource cleanup for every cloud deployment path.
- Put reusable presentation behavior under `shared/`.
- Update the template and validator together when changing the package contract.
- Preserve the root workshop paths. The Foundry IQ catalog entry is a presentation layer over
  the existing workshop rather than a second copy of it.
