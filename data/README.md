# Sample Data

This folder contains the synthetic content used to build the Foundry IQ workshop's Azure AI Search indexes and knowledge bases.

## Contents

| Path | Purpose |
|:-----|:--------|
| `ai-search-data/filesource/` | File content uploaded directly as a knowledge source in the notebook flow |
| `ai-search-data/hrdocs/` | Human-resources source documents, including the Zava company overview |
| `ai-search-data/healthdocs/` | Health-plan and benefits source documents |
| `index-data/index.json` | Exported Azure AI Search index definition used as the restore template |
| `index-data/hrdocs-exported.jsonl` | Pre-chunked HR records loaded into the `hrdocs` index |
| `index-data/healthdocs-exported.jsonl` | Pre-chunked health records loaded into the `healthdocs` index |

## How It Is Used

During `azd up`, `infra/create-knowledge.py` reads `index-data/index.json`, updates the vectorizer endpoint for the deployed Microsoft Foundry resource, creates the two indexes, and uploads the JSONL records. The notebooks then create knowledge sources over those indexes.

`notebooks/restore.ipynb` provides the same restore capability for an existing workshop environment.

## Reusing Or Replacing The Data

The exported JSONL records must match the fields and vector dimensions defined by `index.json`. If you replace the sample documents, regenerate compatible chunks and embeddings rather than editing individual exported records by hand.

Keep sample data synthetic and suitable for broad internal or public distribution. Do not add customer data, employee data, credentials, access tokens, or confidential Microsoft information.
