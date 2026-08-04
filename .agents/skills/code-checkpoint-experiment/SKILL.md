---
name: code-checkpoint-experiment
description: Run or advance a frontend, backend, or infrastructure experiment in this repository using a small stacked PR chain for design, independent review, and implementation, while filing concrete out-of-scope findings as GitHub issues. Use when creating an experiment, reviewing its intermediate design, implementing an approved design, recording results, or discovering follow-up work.
---

# Code checkpoint experiment

Keep the workflow small. Work in exactly one of `frontend/`, `backend/`, or `infra/` at a time, and do not couple the areas.

## Choose the task

Choose one representative task that fits in a focused implementation PR. Define a concrete outcome and a few acceptance criteria. Avoid building shared experiment infrastructure.

Use this minimal area structure:

```text
<area>/
├── design.md
├── review.md
└── <implementation files>
```

## Create the PR chain

Create three stacked branches and PRs:

1. `agent/<area>-design`, based on `main`
2. `agent/<area>-review`, based on the design branch
3. `agent/<area>-implementation`, based on the review branch

Merge them in the same order. Keep each PR limited to its checkpoint.

## Design checkpoint

Write only `<area>/design.md`. Include:

- goal
- scope and non-goals
- proposed approach
- acceptance criteria
- verification method
- unresolved decisions

Keep the design at the level needed to choose an approach. Leave ordinary coding details to implementation.

Wait for human approval before starting the review checkpoint.

## Review checkpoint

Review the design from a fresh context. Use only the stated task and `design.md`; do not rely on the design author's conversation.

Check correctness, missing decisions, simplicity, testability, and area-specific risks. Prefer removing unnecessary complexity over covering speculative cases.

Write `<area>/review.md` with:

- issues that should be addressed
- suggestions intentionally rejected and why
- final assessment

Update `design.md` only for accepted findings. Do not add implementation code.

Wait for human approval before implementation.

## Implementation checkpoint

Implement only the approved design. Add the smallest useful tests and GitHub Actions checks needed to prove the code is valid for its area.

If a new product or architecture decision appears, stop and return to the design checkpoint. Do not silently expand the scope.

Before publishing the implementation PR:

1. Run the relevant formatter, linter or static check, tests, and build or validation command.
2. Self-review the complete diff for correctness and unnecessary complexity.
3. Note the first CI failures instead of erasing them from the experiment record.

## File discovered problems

When a concrete problem is discovered and fixing it would expand the current checkpoint or PR, create a GitHub issue without asking for separate approval.

Before creating it, search for an existing issue. Combine closely related findings. Include:

- observed problem
- evidence or relevant location
- why it is outside the current PR
- possible next step

Do not file speculative concerns, style preferences, or problems already fixed by the current change. Continue the current task after filing unless the finding invalidates the approved design or makes implementation unsafe.

## Record the result

After the implementation is verified, add a short result to the repository README covering only:

- problems prevented by design review
- design rework discovered during implementation
- first-run CI failures
- unnecessary complexity found
- whether the three-checkpoint split helped

Do not add a separate reporting framework unless several experiments demonstrate the need.
