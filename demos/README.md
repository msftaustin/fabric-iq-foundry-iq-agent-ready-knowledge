# Reusable demo catalog

Use this catalog to find presentation-ready demos in the repository. Each entry supports two
paths:

- A static browser walkthrough for audiences who do not need to install or deploy anything
- A technical path covering source, setup, deployment, and customization

The catalog table is generated from each demo's `demo.json` file:

```bash
python scripts/demos.py catalog
```

<!-- DEMO-CATALOG:BEGIN -->
| Demo | Summary | Status | Tags | Walkthrough | Deployment |
|:-----|:--------|:------:|:-----|:------------|:-----------|
| [Agent-Ready Knowledge with Foundry IQ](foundry-iq-agent-ready-knowledge/) | Build citation-backed enterprise knowledge across Azure AI Search, Web IQ, Fabric IQ, and Work IQ. | ready | `foundry-iq`, `azure-ai-search`, `fabric-iq`, `work-iq`, `python` | [Open](foundry-iq-agent-ready-knowledge/walkthrough/index.html) | [azure, fabric, azure-developer-cli](foundry-iq-agent-ready-knowledge/infra/README.md) |
<!-- DEMO-CATALOG:END -->

To contribute another scenario, follow the [contribution guide](../CONTRIBUTING.md).
