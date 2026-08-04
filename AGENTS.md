# Repository guidance

This repository explores where human review checkpoints improve AI-generated code.

## Keep the experiment small

- Keep `frontend/`, `backend/`, and `infra/` independent.
- Prefer one small, representative task per area over a connected sample system.
- Add only the files, dependencies, and tooling needed for the current experiment.
- Do not introduce an experiment framework, metadata format, or reporting system until repeated work proves it useful.

## Work in checkpoints

- Use the `code-checkpoint-experiment` skill for experiment work.
- Create a stacked PR chain for each area in this order: design, review, implementation.
- Do not include implementation code in the design or review PR.
- Treat human approval of each checkpoint as required before starting the next one.
- Stop and ask when implementation requires a product or architecture decision not settled by the approved design.

## Verify generated code

- Add the smallest relevant automated checks with the implementation.
- Frontend should eventually cover formatting, linting, type checking, tests, and build validity.
- Backend should eventually cover formatting, static checks, and tests.
- Infra should eventually cover formatting, validation, and linting without requiring cloud credentials.
- Record first-run CI failures; they are experiment results, not merely cleanup work.

## Review priorities

- Check correctness, scope, simplicity, and testability.
- Flag unnecessary abstraction, generalization, dependencies, and speculative edge cases.
- Keep rejected review suggestions in the record with a short reason.
