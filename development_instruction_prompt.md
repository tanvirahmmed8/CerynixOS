# Development Instruction Prompt

Use this prompt for all future CerynixOS development work.

## Prompt
You are building CerynixOS, an enterprise AI operating system.

Follow these rules:
* Keep outputs short and high signal.
* Follow existing architecture and milestone scope.
* Prefer simple, testable, modular code.
* Do not break folder boundaries.
* Do not add hidden behavior, magic defaults, or silent side effects.
* If a feature changes behavior, update its docs in the same task.
* When a feature is finished, document it inside that feature's folder.
* Write docs so a new engineer can understand the folder without reading all code.
* If code and docs conflict, fix the docs before closing the task.

## Coding Standard
* Small files and focused modules
* Clear names over clever names
* Config over hardcoded values
* Safe defaults
* Explicit error handling
* Logs must be useful and structured
* Public interfaces must be stable and documented
* Security-sensitive code must state assumptions and limits
* Add tests for business logic and risky flows
* Avoid dead code, TODO clutter, and unused dependencies

## Required Folder Docs
Each feature folder should contain:
* `README.md` for purpose, flow, inputs, outputs, and key files
* `CHANGELOG.md` for completed feature notes

Keep both small.

### `README.md` format
* What this folder does
* Main components
* Data flow
* External dependencies
* Risks or limits

### `CHANGELOG.md` format
* Date
* Feature name
* What was added or changed
* Any migration, policy, or API impact

## Completion Rule
A task is not done until:
* code is implemented
* tests are updated if needed
* folder docs are updated
* behavior changes are explained briefly

## Output Style
When reporting work:
* say what changed
* say what docs were updated
* say any risk or follow-up

Keep the response compact.
