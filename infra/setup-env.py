"""
Write all environment variables needed by notebooks into the repo root .env file.
Fetches API keys (not available as Bicep outputs) via the management REST API
using AzureCliCredential (az token) — this matches the interactive deployment shell.
"""
import os
from pathlib import Path

import requests
from azure.identity import AzureCliCredential
from dotenv import dotenv_values

env_path = Path(__file__).parents[1] / ".env"
existing_env = dotenv_values(env_path)
fabric_capacity_resource_id = os.environ.get("FABRIC_CAPACITY_ID", "")
existing_capacity_resource_id = existing_env.get("FABRIC_CAPACITY_RESOURCE_ID", "")
same_fabric_deployment = bool(
    fabric_capacity_resource_id
    and (
        existing_capacity_resource_id == fabric_capacity_resource_id
        or not existing_capacity_resource_id
    )
)


def preserved_fabric_value(name, default=""):
    if not same_fabric_deployment:
        return default
    return existing_env.get(name) or default

# Fetch API keys via management REST API
cred = AzureCliCredential()
token = cred.get_token("https://management.azure.com/.default").token

sub = os.environ["AZURE_SUBSCRIPTION_ID"]
rg = os.environ["AZURE_RESOURCE_GROUP"]
headers = {"Authorization": f"Bearer {token}"}


def post(url):
    response = requests.post(url, headers=headers, timeout=120)
    response.raise_for_status()
    return response.json()


search_name = os.environ["AZURE_SEARCH_SERVICE_NAME"]
search_key = post(
    f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}"
    f"/providers/Microsoft.Search/searchServices/{search_name}"
    f"/listAdminKeys?api-version=2023-11-01"
)["primaryKey"]

openai_name = os.environ["AZURE_OPENAI_SERVICE_NAME"]
openai_key = post(
    f"https://management.azure.com/subscriptions/{sub}/resourceGroups/{rg}"
    f"/providers/Microsoft.CognitiveServices/accounts/{openai_name}"
    f"/listKeys?api-version=2023-05-01"
)["key1"]

# Write .env with all values
env_path.write_text(
    f"""\
# Azure AI Search Configuration
AZURE_SEARCH_SERVICE_ENDPOINT={os.environ['AZURE_SEARCH_SERVICE_ENDPOINT']}
AZURE_SEARCH_ADMIN_KEY={search_key}

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT={os.environ['AZURE_OPENAI_ENDPOINT']}
AZURE_OPENAI_KEY={openai_key}
AZURE_OPENAI_CHATGPT_DEPLOYMENT={os.environ['AZURE_OPENAI_CHATGPT_DEPLOYMENT']}
AZURE_OPENAI_CHATGPT_MODEL_NAME=gpt-5.4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT={os.environ['AZURE_OPENAI_EMBEDDING_DEPLOYMENT']}

# Tenant and project configuration
AZURE_TENANT_ID={os.environ['AZURE_TENANT_ID']}

# Fabric configuration (populated by lakehouse setup if capacity was deployed)
FABRIC_CAPACITY_ID={fabric_capacity_resource_id}
FABRIC_CAPACITY_RESOURCE_ID={fabric_capacity_resource_id}
FABRIC_WORKSPACE_ID={preserved_fabric_value('FABRIC_WORKSPACE_ID')}
FABRIC_ONTOLOGY_ID={preserved_fabric_value('FABRIC_ONTOLOGY_ID')}
FABRIC_WORKSPACE_NAME={preserved_fabric_value('FABRIC_WORKSPACE_NAME')}
FABRIC_ONTOLOGY_NAME={preserved_fabric_value('FABRIC_ONTOLOGY_NAME')}
FABRIC_LAB_USER_UPN={os.environ.get('FABRIC_LAB_USER_UPN', preserved_fabric_value('FABRIC_LAB_USER_UPN'))}
FABRIC_LAB_USER_OID={os.environ.get('FABRIC_LAB_USER_OID', preserved_fabric_value('FABRIC_LAB_USER_OID'))}
CREATE_ONTOLOGY={preserved_fabric_value('CREATE_ONTOLOGY', 'true')}
INCLUDE_EMBEDDINGS={preserved_fabric_value('INCLUDE_EMBEDDINGS', 'false')}
""",
    encoding="utf-8",
)

print("Created .env file")
