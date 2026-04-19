# Requirements — Phase 9: React Operator Dashboard

_Branch: `phase-9-react-operator-dashboard` | Date: 2026-04-19_

---

## Scope

### Included

A single-page React 18 + TypeScript operator dashboard at `services/ui/` that:

1. **Query input** — text field + Submit button; disabled while a request is
   in flight
2. **Result panel** — displays status, intent, and agent_result for the most
   recently submitted query; polls `GET /result/{task_id}` every 1 second until
   status is no longer `"pending"`, then stops
3. **Audit log table** — paginated (10 rows per page) table of every task
   submitted in the current session, accumulated in React state; columns:
   Task ID (truncated UUID), Intent, Status, Agent Result (truncated)
4. **Loading and error states** — spinner while pending; inline error message
   on network failure; "Task not found" on 404
5. **Smoke test** — manual walkthrough against the running API service
   (see `validation.md`)

### Not included

- Authentication / authorisation (no login screen)
- Real-time server push (WebSocket / SSE) — poll model is sufficient
- Persistent audit log across page reloads (session state only)
- Historical audit log fetched from a `GET /tasks` API endpoint — deferred
  to Phase 10 once RDS is wired
- Dark mode, theming, or responsive mobile layout
- End-to-end automated browser tests (Playwright / Cypress) — deferred

---

## Field / data table

| UI element | Data source | API field |
|------------|-------------|-----------|
| Task ID | POST /query response | `task_id` |
| Status | GET /result poll | `status` |
| Intent | GET /result poll | `intent` |
| Agent result | GET /result poll | `agent_result` (JSON-stringified) |
| Error message | GET /result poll | `error` |

Audit log row = `{ task_id, status, intent, agent_result }` stored in
`useState<TaskRow[]>` — one entry appended per completed poll.

---

## Decisions

| Decision | Choice | Reason |
|----------|--------|--------|
| App location | `services/ui/` | Mirrors `services/api/` and `services/central/` structure |
| Scaffold tool | Vite + React + TypeScript template | Fastest zero-config setup; no CRA; matches Node.js 20 LTS requirement from tech-stack.md |
| Component approach | Plain React functional components + hooks | No state management library needed for a single session; no router needed for single-page layout |
| Polling interval | 1 000 ms | Responsive UX without hammering the API |
| Polling stop condition | `status !== "pending"` | Matches consumer.py idempotency logic |
| Audit log data | React `useState` (session memory) | No `GET /tasks` endpoint exists yet; RDS-backed history deferred to Phase 10 |
| Pagination | 10 rows, client-side | Simple slice; no server pagination needed for session data |
| API base URL | `VITE_API_URL` env var, default `http://localhost:8000` | Allows docker compose override without code changes |
| Styling | Plain CSS (no framework) | No Tailwind or MUI added per tech-stack constraints; spec does not require a visual framework |
| Error boundary | Inline `try/catch` in fetch handlers | No React ErrorBoundary needed for this scope |

---

## Context

- **Stack pointers**: React 18, TypeScript 5.x, Vite, Node.js 20 LTS — all
  from `specs/tech-stack.md`. Do not add new npm dependencies without user
  approval.
- **API contract**: `POST /query` accepts `{ query: string }`, returns
  `{ task_id, status, intent, agent_result, error }`. `GET /result/{task_id}`
  returns the same shape. Defined in `services/api/models.py` and
  `specs/2026-04-19-fastapi-service/requirements.md`.
- **Validation requirement**: `query` must be non-empty and non-whitespace —
  the API returns 422 if blank. The UI must enforce this client-side and show
  an inline validation message rather than hitting the API.
- **Audit log source**: Each task row is appended to local state once polling
  resolves (status changes from `"pending"`). No separate fetch.
- **Smoke test is the acceptance gate**: No automated browser tests in this
  phase. The definition of done is a passing manual walkthrough (see
  `validation.md`).
