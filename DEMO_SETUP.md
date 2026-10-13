# Prepare the Foundry IQ customer-demo environment

This runbook is for Microsoft employees preparing the demo in a Microsoft-controlled Azure and
Fabric tenant. Customers are the audience, not the operators of this repository. Use a dedicated
demo tenant, demo identity, and synthetic content. Do not sign in with a customer account or use
personal mailbox data.

The deployment creates billable Azure and Fabric resources and uses public endpoints and local
API-key authentication for demo convenience. It is not a production deployment guide.

## What Gets Deployed

`azd up` deploys and configures:

- Azure AI Search with the `hrdocs` and `healthdocs` sample indexes
- A Microsoft Foundry account and project
- `gpt-5.4` and `text-embedding-3-large` model deployments
- A Microsoft Fabric capacity, workspace, lakehouse, sample tables, and ontology
- A local, Git-ignored `.env` containing the endpoints and credentials used by the notebooks

Parts 1 and 3 are the core Azure+Fabric demo flow. Part 2 optionally adds Web IQ. Parts 4 and 5
optionally require Work IQ with approved synthetic Microsoft 365 demo content and a dedicated
demo identity.

## Prerequisites

- **Azure subscription** with sufficient permissions to create resources
- **Azure Developer CLI (azd)** installed ([Install guide](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd))
- **Azure CLI** installed and configured ([Install guide](https://learn.microsoft.com/cli/azure/install-azure-cli))
- **Python 3.10 or later** installed and available as `py` or `python` on Windows, or `python3` on macOS/Linux
- **Git** (to clone this repository)
- **VS Code** with the Jupyter extension (recommended)

Verify the local tools before continuing:

```powershell
az version
azd version
python --version
git --version
```

On macOS/Linux, use `python3 --version` if `python` is not available.

The post-provision hook creates `.venv` automatically when it is missing and installs the pinned notebook dependencies into it. Creating and activating it yourself is still recommended so VS Code and the notebooks use the same interpreter.

### Required Azure Permissions

You'll need permissions to:

- Create resource groups
- Deploy Bicep templates
- Create and manage:
  - Azure AI Search services
  - Microsoft Foundry projects
  - Azure OpenAI model deployments
- Assign Azure RBAC roles

In practice, use an account with **Contributor** and **User Access Administrator** on the target subscription or resource group. Parts 3 and 5 also require permission to create and administer Microsoft Fabric capacity and workspace items. Tenant policy, regional capacity, or model quota can still prevent deployment even when Azure RBAC is sufficient.

### Tenant Feature Requirements

- **Fabric IQ:** Microsoft Fabric must be enabled for the demo tenant. The deploying user must be
  accepted as the Fabric capacity administrator and be allowed to create workspace items.
- **Work IQ:** Optional. This repository does not provision Work IQ or seed a mailbox. Only enable
  Parts 4–5 when the demo tenant has approved synthetic content and the presenter can use a
  dedicated demo identity.
- **Web IQ:** Optional. Part 2 requires approved Web IQ access. `azd up` does not create this
  entitlement.

> [!NOTE]
> The intended live demo environment includes Fabric. Disabling Fabric capacity makes Parts 3 and
> 5 unavailable.

## Quick Start

### 1. Get the demo repository

```bash
git clone https://github.com/msftaustin/fabric-iq-foundry-iq-agent-ready-knowledge.git
cd foundry-iq-agent-ready-knowledge
```

### 2. Create and activate the Python environment

#### Windows

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

#### Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Provision Azure and Fabric

Authenticate to the approved demo tenant and select the subscription where demo resources are
allowed. Both commands use browser authentication by default.

```bash
az login --tenant "<tenant-id>"
azd auth login --tenant-id "<tenant-id>"
```

Confirm the intended subscription:

```bash
az account show --output table
azd auth login --check-status
```

If needed, select it explicitly:

```bash
az account set --subscription "<subscription name or ID>"
```

Create an azd environment for this demo:

```bash
azd env new foundry-iq
```

Set the deployment regions. `AZURE_LOCATION` is used for Microsoft Foundry and Fabric. Azure AI Search defaults to the tested `westcentralus` region, but you can choose another supported region when tenant policy or capacity requires it.

```bash
azd env set AZURE_LOCATION eastus2
azd env set AZURE_SEARCH_LOCATION westcentralus
```

The Bicep template needs the deploying user's UPN for Fabric administration:

PowerShell:

```powershell
azd env set AZURE_FABRIC_ADMIN_UPN (az account show --query user.name -o tsv)
```

bash/zsh:

```bash
azd env set AZURE_FABRIC_ADMIN_UPN "$(az account show --query user.name -o tsv)"
```

Provision the complete Azure+Fabric demo environment:

```bash
azd env set DEPLOY_FABRIC_CAPACITY true
azd up
```

This provisions and configures:

- Provision AI Search, the Foundry project, and model deployments
- Provision Fabric capacity, workspace content, lakehouse, and ontology
- Fetch API keys and write a `.env` file with all required variables
- Create search indexes and upload sample data

The command may prompt for environment values not set above. Resource names are generated from
the environment and resource-group identity. Deployment can take several minutes, especially
while Fabric items and model deployments become available.

### 4. Validate the Deployment

Successful post-provisioning prints `Postprovision complete` and creates a `.env` in the repository root. Do not commit this file.

Check that required configuration is present without printing secret values:

```powershell
.venv\Scripts\python.exe -c "from dotenv import dotenv_values; required=['AZURE_SEARCH_SERVICE_ENDPOINT','AZURE_SEARCH_ADMIN_KEY','AZURE_OPENAI_ENDPOINT','AZURE_OPENAI_KEY','AZURE_OPENAI_CHATGPT_DEPLOYMENT','AZURE_OPENAI_EMBEDDING_DEPLOYMENT','AZURE_TENANT_ID']; values=dotenv_values('.env'); missing=[name for name in required if not values.get(name)]; print('Configuration ready' if not missing else 'Missing: ' + ', '.join(missing))"
```

For a full Fabric deployment, also confirm `FABRIC_WORKSPACE_ID` and `FABRIC_ONTOLOGY_ID` are present:

```powershell
.venv\Scripts\python.exe -c "from dotenv import dotenv_values; values=dotenv_values('.env'); missing=[name for name in ['FABRIC_WORKSPACE_ID','FABRIC_ONTOLOGY_ID'] if not values.get(name)]; print('Fabric configuration ready' if not missing else 'Missing: ' + ', '.join(missing))"
```

On macOS/Linux, replace `.venv\Scripts\python.exe` with `.venv/bin/python`.

You can also verify the indexes in the Azure portal. Open the deployed Azure AI Search service and confirm that `hrdocs` and `healthdocs` exist and contain documents.

### 5. Run the live demo

1. Open the [notebooks](notebooks) folder in VS Code.
1. Select the Python interpreter from `.venv` as the notebook kernel.
1. Start with `part1-standard-foundry-iq-kb.ipynb`.
1. Run Parts 1 and 3 for the core Azure+Fabric flow.
1. Run Parts 2, 4, and 5 only when the demo tenant has the required Web IQ and approved
   synthetic Work IQ sources.

Later notebooks reuse resources from earlier parts. If the search indexes were deleted or setup was interrupted, run `notebooks/restore.ipynb` before restarting Part 1.

## Troubleshooting

### Azure CLI Authentication Fails During Post-Provisioning

Run `az login`, verify `az account show` points to the selected subscription, then rerun:

```bash
azd hooks run postprovision
```

The hook is safe to retry after a partial setup. It updates the Search indexes and reuses the Fabric workspace, lakehouse, and ontology recorded in the root `.env`. When a different Fabric capacity is provisioned in the same checkout, stale Fabric item IDs are cleared automatically.

### Model Deployment Reports Quota Or Regional Availability Errors

Select a region where both required models are available and your subscription has quota. Use a different azd environment or remove the failed environment after cleanup rather than editing generated resource names.

### Azure AI Search Is Unavailable In The Default Region

Choose a supported Search region and rerun provisioning:

```bash
azd env set AZURE_SEARCH_LOCATION "<search-region>"
azd provision
azd hooks run postprovision
```

### Fabric Setup Fails

Confirm Fabric is enabled in the tenant, the signed-in Azure CLI user matches `AZURE_FABRIC_ADMIN_UPN`, and the user can create Fabric workspaces and ontology items. Review `infra/create-lakehouse.log`, which is generated locally and ignored by Git.

### A Notebook Reports Missing Environment Variables

Confirm `.env` exists at the repository root and run the validation commands above. If Azure resources exist but `.env` is missing, rerun the post-provision hook:

```bash
azd hooks run postprovision
```

### Interactive Sign-In Opens The Wrong Tenant

Sign out of other Microsoft accounts in the browser or use a private browser window. The
interactive identity used by the Fabric and optional Work IQ demo flows must belong to the demo
tenant and have access to the relevant resources. Never use a customer's identity.

## Cleanup

Delete resources when the demo environment is no longer needed to stop ongoing charges:

```bash
azd down --purge --force
```

Confirm the prompt for the same environment used by `azd up`. Then verify the resource group is gone in the Azure portal. Fabric deletion can take longer than the Azure resource-group deletion. If Fabric capacity remains, see the cleanup guidance in the [infrastructure guide](infra/README.md).

Local files such as `.env`, `.venv`, and generated logs are ignored by Git. Remove them manually when you no longer need the local environment.

## Security Boundary

This repository is for controlled demos, not production workloads. It provisions public endpoints
and uses key-based notebook authentication to simplify the demonstration. Use only synthetic
content and non-customer test identities. Do not repurpose this environment for production or
customer data.

## Additional Resources

- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Microsoft Foundry Community Discord](https://aka.ms/AIFoundryDiscord-Ignite25)
