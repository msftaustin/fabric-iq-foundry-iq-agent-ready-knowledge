# Extending Agent-Ready Knowledge with Foundry IQ

Use these extension points to adapt the workshop while preserving its progressive five-part
learning flow.

## Extension points

- **Scenario and presenter story:** Update
  [`../walkthrough/index.html`](../walkthrough/index.html) and
  [`../walkthrough/README.md`](../walkthrough/README.md) for the audience. Keep business claims
  aligned with what the technical lab demonstrates.
- **Documents and indexes:** Replace or add sample content under
  [`../../../data/`](../../../data/) and update the index setup in
  [`../../../infra/`](../../../infra/).
- **Knowledge sources:** Adapt the source configuration in
  [`../../../notebooks/`](../../../notebooks/) one part at a time. Preserve citations and source
  attribution in the resulting experience.
- **Deployment:** Extend [`../../../infra/main.bicep`](../../../infra/main.bicep) and the
  lifecycle hooks only when the new scenario requires additional resources.
- **Workshop guidance:** Keep [`../../../README.md`](../../../README.md),
  [`../../../workshop/README.md`](../../../workshop/README.md), and
  [`../../../deploy_yourself.md`](../../../deploy_yourself.md) synchronized with behavior changes.

## Ideas

- Replace the Zava scenario with an approved customer or industry scenario.
- Add another governed document corpus and compare retrieval behavior.
- Add a new knowledge source in a separate notebook before combining it in the capstone.
- Capture approved screenshots in `../walkthrough/assets/` for a richer offline presentation.
- Scaffold a separate demo with `python scripts/demos.py new <demo-id> --title "<title>"` when the
  scenario has its own source, infrastructure, or deployment lifecycle.
