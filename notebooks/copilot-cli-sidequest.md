# Copilot CLI sidequest: use your KB as an MCP server

Every Foundry IQ knowledge base exposes an MCP server, and you can use GitHub Copilot CLI to ask questions that can be answered by that MCP server. Follow the instructions here to set up Copilot CLI.

## 1. Sign in to GitHub

Sign in to GitHub with an account that has access to GitHub Copilot. If your organization uses single sign-on, authorize the account through your organization's standard SSO process.

## 2. Sign in to GitHub Copilot CLI

Open the Terminal in VS Code (Terminal > New Terminal).

Sign in to GitHub Copilot CLI:

```powershell
copilot login
```

As part of the authorization step, you will be prompted to enter an 8-digit device code that is printed in the terminal.


## 3. Add the KB MCP server

Run the command printed by the notebook checkpoint cell. It will look like this:

```powershell
copilot mcp add zava-kb "<KB MCP URL>" --header "api-key=<SERVICE KEY>"
```

When it succeeds, you will see output like this:

```
Added server "zava-kb"

zava-kb
  Type: http
  URL: https://your-search-service.search.windows.net/knowledgebases/multisource-search-knowledge-base/mcp?api-version=2026-05-01-preview
  Headers:
    api-key: ***
  Tools: * (all)
  Source: User
```

## 4. Ask a question grounded by the KB

Ask Copilot a question that matches the notebook you just ran. For example:

```powershell
copilot -i "Use the Zava knowledge base to answer: what health benefits are available?"
```

You can try asking the question without prefacing it with "Use Zava knowledge base to answer", but the Copilot CLI agent may not choose to invoke the KB MCP server, as it may answer from its weights or using a different tool.
