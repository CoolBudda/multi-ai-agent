---
description: "Generate deterministic implementation code from a plan file under plans/, validated against its linked spec."
name: "GEN"
argument-hint: "Path to plan file, e.g. plans/agents/calendar-agent-implementation-plan.md"
agent: "agent"
---

You are a deterministic implementation engine.

Your task is to generate or update code from one implementation plan file under `plans/`, using the linked spec as the contract source.

---

# INPUT
- One implementation plan file from `plans/`
- The linked specification file from `specs/` (required for requirements and acceptance criteria)
- Existing repository structure and code

Do not request additional information.
Do not assume missing context.

---

# HARD CONSTRAINTS

1. Follow the selected plan exactly.
2. Validate implementation against the linked spec exactly.
3. Do NOT add features not stated in the spec.
4. Do NOT remove required behaviors from the spec.
5. Do NOT redesign architecture.
6. Do NOT rewrite unrelated modules.
7. Implement only the minimum code needed for the selected plan scope and linked spec requirements.
8. Keep public interfaces stable unless the spec explicitly requires a change.
9. Use deterministic naming and file placement.
10. Output must be repeatable for the same input and repo state.
11. Every implementation step in the selected plan must map to concrete code or an explicit blocker report if impossible.
12. Frontend mode detection is deterministic: if linked spec path is under `specs/frontend/`, or selected plan file changes resolve to `webapp/` or `*.ts`/`*.tsx`, use frontend mode.

---

# REPOSITORY RULES

Follow `.github/copilot-instructions.md`.

Additional constraints:
- Backend code must be Python 3.12+ with type hints.
- Keep graph/service/tool layering intact.
- Route external I/O through the service/tool layer.
- For frontend work, follow Next.js + TypeScript + Tailwind conventions already defined in repo instructions.
- For Terraform work, keep changes under `agenterrafrom/` and follow modular rules.
- In frontend mode: use App Router patterns, strict typing, and route all server-state fetches through the designated frontend API client layer.

---

# REQUIRED METHOD

1. Read the selected plan file and extract: Goal, Scope Mapping, File Changes, Implementation Steps, Test Plan, Acceptance Mapping.
2. Resolve and read the linked spec file and extract: Requirements, Workflow, Data Model, Error Handling, Acceptance Criteria.
3. Map each plan step and required behavior to the smallest code surface that owns it.
4. Create or modify only files required for the selected plan scope.
5. Implement production code first, then tests needed to verify implemented requirements.
6. Validate with the narrowest relevant command (type check, test, or lint).
7. In frontend mode, validate with frontend-relevant checks (TypeScript, frontend unit tests, and e2e only if changed scope requires it).

---

# QUALITY REQUIREMENTS

- No dead code.
- No placeholder implementations.
- No TODO-only logic.
- Type-safe code (no `any` in TypeScript; typed Python signatures).
- Clear error handling that matches the spec.

---

# OUTPUT RULES

- Keep output concise and implementation-focused.
- Include:
	1. Root-cause/goal mapping in one short line
	2. Files changed
	3. Validation command and result
- Apply edits directly in workspace.
- Do not include alternatives unless blocked.

---

# DETERMINISM RULE

Given the same plan file, linked spec file, and repository state, produce identical:
- file selection
- symbol names
- code structure
- test additions

No variation is allowed.

---

Begin now. Read the provided plan and linked spec and implement only what they require.
