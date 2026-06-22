# AGENTS.md

## Scope

This repository contains only AI agents for code review automation. It does not host developer agents, feature builders, refactoring assistants, or general-purpose implementation copilots.

Any agent defined here must behave as a reviewer of pull requests and stay within review scope.

## Repository model

- Agents can vary by stack, such as React, Quarkus, or architecture review.
- The workflow is responsible for selecting which agent to run.
- The execution must use the exact agent requested by the workflow input.
- Silent fallback to a different agent is not allowed.
- If the requested agent does not exist, the execution must fail explicitly.
- Limit all executions to pull request review; agents must not implement features or edit the codebase during review flows.
- Review guidance should be retrieved from configured guidance sources and MCP servers when needed, instead of loading the full corpus into the prompt.
- Stack-specific behavior must come from the selected profile under `.github/agents/`.

## Execution rules

- In CI or workflow-driven execution, use the exact agent selected by the workflow input.
- Do not replace the requested agent with a default or inferred agent.
- If the selected agent profile is missing, fail explicitly instead of continuing with another reviewer.
- Do not disclose sensitive information in review output.

## Expected review process

The standard review flow is:

1. Inspect the PR diff artifacts selected by the workflow.
2. Identify the changed files, affected areas, and likely risk surface.
3. Query the configured knowledge source for conventions and review criteria relevant to those changes.
4. Contrast the observed changes against the retrieved guidance.
5. Produce a concise Markdown review comment with findings only when they are evidence-based.
