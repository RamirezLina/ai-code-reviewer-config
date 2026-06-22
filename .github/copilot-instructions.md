# Copilot Instructions

Use the repository rules from `AGENTS.md` as the primary stable policy for any review task in this repository.

Additional operating rules:

- This repository hosts code review agents only, not developer assistants.
- In CI or workflow-driven execution, use the exact agent selected by the workflow input.
- Do not replace the requested agent with a default or inferred agent.
- If the selected agent profile is missing, fail explicitly instead of continuing with another reviewer.
- Limit the task to pull request review; do not implement features, edit the codebase, or disclose sensitive information.
- When review guidance is not already present in the immediate prompt context, consult the agent's configured MCP/RAG sources instead of loading the full corpus into the prompt.

For stack-specific behavior, follow the selected profile in `.github/agents/`.
