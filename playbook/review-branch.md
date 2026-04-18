Do a deep review of all changes on this branch${{ "focusing on: " + ($ARGUMENTS || "the full diff") }}. Spawn multiple subagents to analyze the diff from three different perspectives in parallel:

1. **Correctness & Logic** — Are there bugs, edge cases, or logic errors? Does the code do what it claims?
2. **Design & Architecture** — Does this fit the existing patterns? Any abstractions that are off, over-engineered, or missing?
3. **Product & Requirements** — Do the changes actually match the intent in specs/? Check specs/roadmap.md and any relevant specs/*/requirements.md for the current phase.

For each perspective, surface:
- Anything that doesn't make sense
- Anything that could be done better
- Any missing pieces

Synthesize findings into a final summary with prioritized action items.