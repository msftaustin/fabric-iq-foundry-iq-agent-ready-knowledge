# Demo Environment Infrastructure

This directory provisions the Azure and Fabric resources used by the live customer demo. The
supported setup is documented in the root [demo environment runbook](../DEMO_SETUP.md).

## Provisioning Flow

```text
azd up
  -> main.bicep
  -> postprovision hook
     -> setup-env.py
     -> create-knowledge.py
     -> create-lakehouse.py
```

The deployment creates Azure AI Search, a Microsoft Foundry account and project, model
deployments, role assignments, and Fabric capacity. The post-provision hook writes local
configuration, restores the synthetic search indexes, and creates the Fabric workspace content.

## Core Files

| File | Responsibility |
|:-----|:---------------|
| `main.bicep` | Provisions Azure AI Search, Foundry, model deployments, RBAC, and Fabric capacity |
| `main.parameters.json` | Connects azd environment values to Bicep parameters |
| `hooks/postprovision.ps1` | Runs setup after provisioning on Windows |
| `hooks/postprovision.sh` | Runs setup after provisioning on Linux and macOS |
| `setup-env.py` | Gets service keys through the signed-in Azure identity and writes the ignored root `.env` |
| `create-knowledge.py` | Restores synthetic HR and health indexes from `data/index-data/` |
| `create-lakehouse.py` | Creates Fabric workspace items, loads the Zava dataset, and creates the ontology |

## Local Setup Artifacts

Setup generates values and logs locally. These must remain untracked:

- Root `.env`
- Root `.venv/`
- `create-lakehouse.log` and `index-creation.log`

Never paste secrets or the contents of `.env` into source files, issues, or shared demo material.

## Retry Provisioning

If provisioning succeeded but local setup failed, authenticate to the intended demo tenant and
rerun the hook:

```bash
az login
azd hooks run postprovision
```

Review the generated logs first. The setup scripts update existing indexes and reuse Fabric
workspace items when possible.

## Cleanup

Remove resources created by this azd environment:

```bash
azd down --purge --force
```

Verify that Fabric capacity and tenant-scoped resources are also removed. See the
[cleanup checks](../DEMO_SETUP.md#cleanup) in the runbook.

## Security Scope

This deployment is a controlled demonstration, not a production architecture. It enables public
network access and uses local keys for notebook calls. Do not use customer data, customer
identities, or production resources in this environment.
