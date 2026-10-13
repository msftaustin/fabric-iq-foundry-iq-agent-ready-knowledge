# Deploying Agent-Ready Knowledge with Foundry IQ

Infrastructure remains in the repository's [`infra/`](../../../infra/) folder and uses the root
[`azure.yaml`](../../../azure.yaml) entry point. Keeping those paths stable preserves the
existing Azure Developer CLI lifecycle hooks and notebook setup.

## Options

| Target | Steps |
|---|---|
| Instructor-provided environment | Follow the [guided workshop](../../../workshop/README.md). |
| Your Azure environment | Follow the complete [self-deployment guide](../../../deploy_yourself.md). |

## Self-deployment

Review all prerequisites, supported tenant capabilities, security notes, and cost guidance before
running:

```bash
az login
azd auth login
azd up
```

The deployment writes environment-specific values to the local `.env` file. Never commit or
share that file.

## Clean up

Delete the resources created by Azure Developer CLI:

```bash
azd down --purge --force
```

Complete the [cleanup verification steps](../../../deploy_yourself.md#cleanup) because Fabric
capacity and tenant-scoped resources may require separate confirmation.
