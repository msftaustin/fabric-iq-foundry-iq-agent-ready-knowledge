# Deploying Agent-Ready Knowledge with Foundry IQ

Infrastructure is in the repository's [`infra/`](../../../infra/) folder and uses the root
[`azure.yaml`](../../../azure.yaml) entry point. Keeping those paths stable preserves the
Azure Developer CLI hooks and notebook setup.

## Microsoft Presenter Setup

Use the [demo environment runbook](../../../DEMO_SETUP.md) to provision in an approved
Microsoft-controlled demo tenant. The intended configuration includes Azure AI Search, Foundry,
and Fabric.

The deployment writes tenant-specific values and service keys to the local `.env` file. It is
Git-ignored. Never commit or share it. Work IQ and Web IQ access are optional and are not
provisioned by `azd up`.

The deployment writes environment-specific values to the local `.env` file. Never commit or
share that file.

## Clean up

Delete the resources created by Azure Developer CLI:

```bash
azd down --purge --force
```

Complete the [cleanup checks](../../../DEMO_SETUP.md#cleanup) because Fabric capacity and
tenant-scoped resources may require separate confirmation.
