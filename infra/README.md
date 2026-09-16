# Infrastructure Guide

This folder contains the deployment and setup automation for Foundry IQ Agent-Ready Knowledge. Use the repository-root [self-deployment guide](../deploy_yourself.md) for the supported end-to-end experience.

## Supported Self-Deployment Flow

```text
azd up
  -> infra/main.bicep
  -> infra/hooks/postprovision.ps1 or postprovision.sh
     -> install notebooks/requirements.txt
     -> infra/setup-env.py
     -> infra/create-knowledge.py
     -> infra/create-lakehouse.py (when Fabric is enabled)
```

The deployment creates Azure AI Search, a Microsoft Foundry account and project, model deployments, role assignments, and an optional Fabric F2 capacity. The post-provision hook writes local configuration, restores the sample search indexes, and creates the Fabric workspace content.

Both post-provision hooks anchor execution to the repository root, create `.venv` when needed, and stop on dependency or setup failures. Python 3.10 or later is required. `AZURE_SEARCH_LOCATION` controls the Search region and defaults to `westcentralus`.

## Core Files

| File | Purpose |
|:-----|:--------|
| `main.bicep` | Defines Azure AI Search, Microsoft Foundry, model deployments, RBAC, and optional Fabric capacity |
| `main.parameters.json` | Maps azd environment values into the Bicep deployment |
| `hooks/postprovision.ps1` | Runs setup after provisioning on Windows |
| `hooks/postprovision.sh` | Runs setup after provisioning on macOS/Linux and dev containers |
| `setup-env.py` | Retrieves service keys through the signed-in Azure CLI identity and creates the Git-ignored root `.env` |
| `create-knowledge.py` | Restores the `hrdocs` and `healthdocs` indexes from `data/index-data/` |
| `create-lakehouse.py` | Creates or reuses Fabric workspace items, loads the Zava DIY data, and updates `.env` with Fabric IDs |

## Hosted-Lab Automation

These files support the instructor-managed Skillable environment and are not part of the `azd up` self-deployment path:

| File | Purpose |
|:-----|:--------|
| `deploy-background.ps1` | Runs long deployment work outside the Skillable lifecycle timeout |
| `lifecycle_bicep_deployment.ps1` | Generates and starts the Skillable background deployment |
| `lifecycle_github_repo_download.ps1` | Downloads the repository into the hosted lab VM; optionally uses `GITHUB_TOKEN` |
| `lifecycle_teardown_fabric.ps1` | Removes Fabric capacity from a Skillable-provided resource group |
| `seed-emails.ps1` | Seeds hosted-lab mail data and requires a service principal with Microsoft Graph `Mail.Send` application permission |
| `setup-knowledge.ps1` and `setup-lakehouse.ps1` | Hosted-lab setup wrappers that receive values from lifecycle automation |

Skillable placeholders such as `@lab.CloudResourceGroup(...)` are intentional. Do not run those scripts directly in a self-deployed environment.

## Generated Local Files

The following are generated during setup and must remain untracked:

- Repository-root `.env`
- `infra/.env`
- `.venv/` and `infra/.venv/`
- `infra/create-lakehouse.log`
- `infra/index-creation.log`

Never paste API keys, client secrets, tokens, or the contents of `.env` into issues or documentation.

## Rerun Setup

If Azure provisioning succeeded but local configuration or sample data setup failed, authenticate to Azure CLI and rerun the azd hook:

```bash
az login
azd hooks run postprovision
```

The scripts are designed to create or update the lab resources. Search indexes are updated in place. Fabric item IDs are preserved for retries against the same capacity and reset when the capacity resource changes. Review the generated logs before rerunning if Fabric or index creation failed.

## Cleanup And Recovery

For a self-deployed azd environment, use:

```bash
azd down --purge --force
```

The Skillable teardown script is not a substitute for `azd down`. If a Fabric capacity remains after azd cleanup, locate it in the deployment resource group and delete it from the Azure portal before deleting local azd state.

## Security Scope

This is lab infrastructure. It enables public network access and local API-key authentication to reduce workshop setup friction. Production adaptations should use Microsoft Entra ID, least-privilege resource-scoped roles, restricted networking, an approved secret store, monitoring, and organizational policy controls.
