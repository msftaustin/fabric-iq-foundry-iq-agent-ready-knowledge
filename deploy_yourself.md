# Deploy Foundry IQ Agent-Ready Knowledge

Use this guide to provision and run the Foundry IQ workshop in your own environment. The deployment is intended for learning and demonstration. It creates billable resources and uses public endpoints and local API-key authentication for workshop convenience.

## What Gets Deployed

`azd up` deploys and configures:

- Azure AI Search with the `hrdocs` and `healthdocs` sample indexes
- A Microsoft Foundry account and project
- `gpt-5.4` and `text-embedding-3-large` model deployments
- A Microsoft Fabric capacity, workspace, lakehouse, sample tables, and ontology when Fabric deployment is enabled
- A local, Git-ignored `.env` containing the endpoints and credentials used by the notebooks

Parts 1 and 2 use Azure AI Search and Microsoft Foundry. Parts 3 and 5 require Fabric. Part 4 requires Work IQ access in your tenant and uses content available to your signed-in account.

## Prerequisites

- **Azure subscription** with sufficient permissions to create resources
- **Azure Developer CLI (azd)** installed ([Install guide](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd))
- **Azure CLI** installed and configured ([Install guide](https://learn.microsoft.com/cli/azure/install-azure-cli))
- **Python 3.10 or later** installed and available as `py` or `python` on Windows, or `python3` on macOS/Linux
- **Git** (to clone this repository)
- **VS Code** or **GitHub Codespaces** with Jupyter extension (recommended)

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

- **Fabric IQ:** Microsoft Fabric must be enabled for the tenant. The deploying user must be accepted as the Fabric capacity administrator and be allowed to create workspace items.
- **Work IQ:** Your user and tenant must have access to Work IQ. Self-deployment does not seed mailbox data, so results depend on content the signed-in user can access.
- **Web IQ:** Part 2 requires a Web IQ key or access supplied separately. `azd up` does not create this entitlement.

> [!NOTE]
> To run only the Azure AI Search portions, disable Fabric capacity before deployment. Parts 3 and 5 will not be available.

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-fork-url> foundry-iq-agent-ready-knowledge
cd foundry-iq-agent-ready-knowledge
```

### 2. Create and activate a Python virtual environment

#### Windows (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

#### macOS/Linux (bash/zsh)

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Deploy with azd

Authenticate both CLIs in the same tenant. Both commands use browser authentication by default. Replace `<tenant-id>` with the Microsoft Entra tenant where you will deploy.

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

Create and select an azd environment. Use a short name that identifies your deployment:

```bash
azd env new foundry-iq
```

Set the deployment regions. `AZURE_LOCATION` is used for Microsoft Foundry and Fabric. Azure AI Search defaults to the tested `westcentralus` region, but you can choose another supported region when tenant policy or capacity requires it.

```bash
azd env set AZURE_LOCATION eastus2
azd env set AZURE_SEARCH_LOCATION westcentralus
```

Store the deploying user's UPN in that environment. The Bicep template requires this value even when Fabric capacity deployment is disabled.

PowerShell:

```powershell
azd env set AZURE_FABRIC_ADMIN_UPN (az account show --query user.name -o tsv)
```

bash/zsh:

```bash
azd env set AZURE_FABRIC_ADMIN_UPN "$(az account show --query user.name -o tsv)"
```

Then choose one deployment mode.

#### Full Lab With Fabric

PowerShell:

```powershell
azd env set DEPLOY_FABRIC_CAPACITY true
azd up
```

bash/zsh:

```bash
azd env set DEPLOY_FABRIC_CAPACITY true
azd up
```

#### Azure AI Search Only

This lower-cost path supports Parts 1 and 2. It does not provision the Fabric resources required by Parts 3 and 5.

```bash
azd env set DEPLOY_FABRIC_CAPACITY false
azd up
```

This will:

- Provision AI Search, the Foundry project, and model deployments
- Provision Fabric capacity only when `DEPLOY_FABRIC_CAPACITY` is `true`
- Fetch API keys and write a `.env` file with all required variables
- Create search indexes and upload sample data
- Set up the Fabric Lakehouse with Zava DIY dataset and ontology

The command may prompt for any environment values not set above. Resource names are generated from the environment and resource-group identity. Deployment can take several minutes, especially while Fabric items and model deployments become available.

> **Note:** Email seeding (used in the hosted Skillable lab for Part 4 - Work IQ) requires a service principal with `Mail.Send` application permission and is **not run** during self-deploy. Part 4 will use your own mailbox data instead.

### 4. Validate the Deployment

Successful post-provisioning prints `Postprovision complete` and creates a `.env` in the repository root. Do not commit this file.

Check the azd environment and required configuration without printing secret values:

```powershell
azd env get-values
.venv\Scripts\python.exe -c "from dotenv import dotenv_values; required=['AZURE_SEARCH_SERVICE_ENDPOINT','AZURE_SEARCH_ADMIN_KEY','AZURE_OPENAI_ENDPOINT','AZURE_OPENAI_KEY','AZURE_OPENAI_CHATGPT_DEPLOYMENT','AZURE_OPENAI_EMBEDDING_DEPLOYMENT','AZURE_TENANT_ID']; values=dotenv_values('.env'); missing=[name for name in required if not values.get(name)]; print('Configuration ready' if not missing else 'Missing: ' + ', '.join(missing))"
```

For a full Fabric deployment, also confirm `FABRIC_WORKSPACE_ID` and `FABRIC_ONTOLOGY_ID` are present:

```powershell
.venv\Scripts\python.exe -c "from dotenv import dotenv_values; values=dotenv_values('.env'); missing=[name for name in ['FABRIC_WORKSPACE_ID','FABRIC_ONTOLOGY_ID'] if not values.get(name)]; print('Fabric configuration ready' if not missing else 'Missing: ' + ', '.join(missing))"
```

On macOS/Linux, replace `.venv\Scripts\python.exe` with `.venv/bin/python`.

You can also verify the indexes in the Azure portal. Open the deployed Azure AI Search service and confirm that `hrdocs` and `healthdocs` exist and contain documents.

### 5. Start the Workshop

1. Open the [notebooks](notebooks) folder in VS Code.
1. Select the Python interpreter from `.venv` as the notebook kernel.
1. Start with `part1-standard-foundry-iq-kb.ipynb`.
1. Run each notebook from top to bottom and complete the five parts in order.

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

Sign out of other Microsoft accounts in the browser or use a private browser window. The interactive identity used by Parts 3 through 5 must belong to the same tenant as the deployed resources and have access to the relevant Fabric and Work IQ data.

## Cleanup

Delete resources as soon as you finish to stop ongoing charges:

```bash
azd down --purge --force
```

Confirm the prompt for the same environment used by `azd up`. Then verify the resource group is gone in the Azure portal. Fabric deletion can take longer than the Azure resource-group deletion. If Fabric capacity remains, see the cleanup guidance in the [infrastructure guide](infra/README.md).

Local files such as `.env`, `.venv`, and generated logs are ignored by Git. Remove them manually when you no longer need the local environment.

## Production Use

This repository is a lab, not a production reference architecture. Before adapting it for organizational workloads, replace key-based notebook authentication with Microsoft Entra ID, restrict public network access, use least-privilege scopes for role assignments, store secrets in an approved secret store, and add operational monitoring and policy controls.

## Additional Resources

- [Azure AI Search Documentation](https://learn.microsoft.com/azure/search/)
- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [Microsoft Foundry Community Discord](https://aka.ms/AIFoundryDiscord-Ignite25)
