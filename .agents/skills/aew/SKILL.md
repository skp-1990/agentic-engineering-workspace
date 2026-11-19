---
name: aew
description: "Assess an engineering request from a direct prompt or Jira context, investigate relevant repositories, and produce an evidence-based feasibility plan. Route requests to build, run, resume, or clean up a proof of concept to the poc workflow."
---

# Agentic Engineering Workspace

Turn an engineering request into a concise, reviewable technical discovery report. Accept direct requests, pasted Jira content, or Jira links.

## Choose the workflow

- For a request to perform an end-to-end PoC, compare approaches experimentally, resume a PoC, or clean it up, read the sibling [poc skill](../poc/SKILL.md) and continue through that workflow. Preserve all supplied scope and authorization; do not stop at this skill's discovery report.
- For feasibility/research/planning only, follow the discovery workflow below. Do not execute experiments merely because the request mentions a possible cluster test.
- If a skill loader is unavailable, read the linked files directly. Jira connectors are optional; use available context or request pasted issue details when access is unavailable.

## Inputs

Require a clear objective. Treat the following as optional context:

- Jira key, link, or text;
- component, image, repository, branch, or release;
- scope boundaries and non-goals;
- required validation or live-cluster expectations.

Accept one or more explicit repository URLs or local paths. If none are given, use `repository-resolution` before selecting one. Do not require an OpenShift component mapping for an explicitly supplied project.

## Workflow

Read [workflow.md](references/workflow.md) and follow its phases. Use the sibling [repository-resolution skill](../repository-resolution/SKILL.md) for each relevant repository/ref before making code-level recommendations.

## Safety boundaries

- Do not guess a repository or branch when the evidence is ambiguous.
- Discovery is read-only. An explicit PoC execution request routes to `poc`, which performs the authorized prototype work. Preserve existing authorization across phases; ask only when required details or action scope are missing.
- Clearly separate observed repository evidence from assumptions.
- Keep credentials out of commands, logs, reports, and responses.

## Output

For discovery, return a feasibility report containing the objective, repositories/revisions and confidence, relevant code areas and concepts, recommended approach and alternatives, validation plan, risks and limitations, open questions, and next action. Execution requests use the evidence-backed PoC report instead.
