# Agent-Ready Knowledge with Foundry IQ - presenter script

This script accompanies the no-install [`index.html`](index.html) walkthrough. It is designed
for a non-technical audience and can be presented without Azure access.

## Before you start

- Open `index.html` in a browser.
- Press **F11** for full screen.
- Use the arrow keys to move between steps.
- Press **N** to show or hide presenter notes.
- Allow about one minute per step.

## Story

| Step | What the audience sees | What to say |
|---|---|---|
| 1 | Knowledge is distributed across systems | "The hard part is often not generating text. It is finding the right enterprise context across many systems." |
| 2 | Documents and indexes | "We start with governed content in Azure AI Search and return citations with the answer." |
| 3 | Current web information | "Web IQ adds current external context through a standard MCP connection." |
| 4 | Structured Fabric data | "Fabric IQ contributes business entities and relationships through an ontology." |
| 5 | Workplace context | "Work IQ adds context available to the signed-in user while respecting source access." |
| 6 | Combined answer | "Foundry IQ coordinates these sources and synthesizes one grounded, citation-backed response." |
| 7 | Next step | "A Microsoft presenter can run the technical demo in an approved Azure and Fabric demo tenant." |

## Suggested opening

"Your employees already have the information they need, but it lives in different systems. This
demo shows how Foundry IQ turns those disconnected sources into one grounded knowledge
experience."

## Suggested close

"The live demo builds this pattern one source at a time, so your technical team can see where the
context comes from, how citations are preserved, and where to adapt it for your own scenario."

## Common questions

- **Does the click-through require Azure access?**

  No. It is a static browser experience. The live technical demo requires the services listed in the
  demo prerequisites.
- **Which services are required for the live demo?**

  Azure AI Search, Foundry, and Fabric are used in the core demo. Web IQ and Work IQ are optional
  sources that require separate access and approved demo-tenant data.
- **Is this a production architecture?**

  No. It is a learning and demonstration environment. Production deployments need the
  organization's identity, networking, secret management, monitoring, and governance controls.
- **Can the presenter adapt the scenario?**

  Yes. The extension guide identifies the data, knowledge source, notebook, and infrastructure
  surfaces intended for customization.
