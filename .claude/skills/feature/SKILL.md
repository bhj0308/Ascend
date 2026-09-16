---
name: feature
description: Build a feature end-to-end using parallel subagents that check each other — backend-dev and frontend-dev implement in parallel, then reviewer adversarially challenges the result and findings are fed back until clean. Use when the user asks to build, add, or implement a feature that touches more than one file or both backend and frontend.
user-invocable: true
---

# /feature — parallel build + adversarial review

The main session orchestrates. Subagents do not talk to each other directly; you relay.
Each agent starts cold, so every prompt you write must be self-contained.

## 1. Scope (2–5 lines, no essay)
Read `CLAUDE.md` → Status. Write the acceptance criteria as a checklist:
what must work, what must be rejected (401/403/400), what the UI must show.
If anything is genuinely ambiguous, ask the user now — not after the agents run.

## 2. Fan out (parallel)
Split into backend and frontend work. Spawn **in the same response** whichever apply:
- `backend-dev` — give: criteria, endpoints to add (method, path, auth rule), files to create/modify.
- `frontend-dev` — give: criteria, pages/components, the API endpoints it will call
  (write the request/response shapes into the prompt so it does not have to guess).
Run them in the background; do not predict their results.

## 3. Review (adversarial)
When both report, spawn `reviewer` with: the acceptance criteria, the list of changed files
(`git status --short` + `git diff --stat`), and each agent's report *labelled as claims*.
Ask it to verify every claim by running the code.

## 4. Fix loop (max 2 rounds)
For each BLOCKING finding, use `SendMessage` to the agent that owns the file — this keeps its
context, so it does not re-read the repo. Paste the finding verbatim. Then re-spawn `reviewer`
scoped **only to the fixes** ("re-check findings 1 and 3; do not re-review everything").
Stop after 2 rounds and surface what is still open to the user instead of looping.

## 5. Final verification (you, not an agent)
- `cd frontend && npm run build`
- `cd backend && black --check app/ && isort --check-only app/`
- `/smoke-test` if any API route changed
Report faithfully: what changed, what the reviewer caught, what is verified, what is not.

## Token discipline
- Do not spawn an agent for a single-file change; do it yourself.
- Do not spawn a second implementer agent for the same file.
- Prefer `SendMessage` to an existing agent over a fresh spawn.
