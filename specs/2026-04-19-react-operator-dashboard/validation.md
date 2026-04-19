# Validation — Phase 9: React Operator Dashboard

_Branch: `phase-9-react-operator-dashboard` | Date: 2026-04-19_

---

## Automated checks

### TypeScript

```bash
cd services/ui && npx tsc --noEmit
```

Must pass with zero errors.

### Build

```bash
cd services/ui && npm run build
```

Must complete without errors. Output in `services/ui/dist/`.

### Vite dev server

```bash
cd services/ui && npm run dev
```

Must start without errors. Browser console must show no TypeScript or React
errors on initial load.

---

## Manual walkthrough

> **Note:** Scenarios 1–3 and 5 require the full API + SQS stack. Phase 8
> wired `POST /query` to SQS, so the API returns 500 without a real SQS
> endpoint. These scenarios are **deferred to Phase 10** when LocalStack is
> wired. Scenarios 4 and 6 (client-side validation and network error) can be
> run immediately with just the Vite dev server.

### Prerequisites (full stack — Phase 10+)

1. LocalStack running with SQS queue configured (Phase 10)
2. SQS consumer running: `py -3.11 -m services.central.consumer`
3. API service running: `QUEUE_URL=<localstack-queue-url> uvicorn services.api.main:app --reload`
4. UI dev server running: `npm run dev` from `services/ui/`
5. Browser open at `http://localhost:5173` (Vite default)

### Prerequisites (UI-only — available now)

1. UI dev server running: `npm run dev` from `services/ui/`
2. Browser open at `http://localhost:5173`

---

### Scenario 1 — Happy path: tracking query _(Phase 10+)_

1. Type `where is vessel IMO-001` into the query input.
2. Click Submit (or press Enter).
3. **Expected**: button is disabled; result panel shows `status: pending`
   and a loading indicator.
4. Within ~2 s: result panel updates to `status: completed`,
   `intent: TRACKING`, and `agent_result` shows the stub tool response.
5. Audit log table shows one row: truncated task ID, `TRACKING`, `completed`.
6. Submit button is re-enabled.

### Scenario 2 — Events query _(Phase 10+)_

1. Type `show me recent alerts for zone 3`.
2. Submit.
3. **Expected**: result panel shows `intent: EVENTS` once completed.
4. Audit log now has two rows (newest first).

### Scenario 3 — SOP query _(Phase 10+)_

1. Type `what is the procedure for safe boarding`.
2. Submit.
3. **Expected**: `intent: SOP` in result panel.

### Scenario 4 — Blank / whitespace query validation _(available now)_

1. Leave the input empty and click Submit.
2. **Expected**: inline error `"Query cannot be empty"` appears; no network
   request is made; button does not disable.
3. Type only spaces and click Submit.
4. **Expected**: same inline error.

### Scenario 5 — Pagination _(Phase 10+)_

1. Submit 11 or more distinct queries.
2. **Expected**: first page shows 10 rows; a Next button appears.
3. Click Next.
4. **Expected**: remaining rows shown; Previous button appears.
5. Click Previous.
6. **Expected**: back to first page.
7. Submit a new query; **Expected**: audit log resets to page 1 showing the newest entry.

### Scenario 6 — Network error _(available now)_

1. Stop the API service while the UI is running.
2. Submit a query.
3. **Expected**: after the POST fails, an error message is displayed inline
   (e.g. `"Network error: Failed to fetch"`); the submit button is re-enabled.

---

## Edge cases

| Case | Expected behaviour |
|------|--------------------|
| Submit while a query is in flight | Submit button is disabled — not possible |
| Result panel before first submit | Shows placeholder (no task yet) |
| `agent_result` is null | Panel shows `null` or omits the field gracefully |
| `error` field set on completed task | Displayed in red below status |
| Task ID in audit log | First 8 chars + `…` |
| Agent result in audit log | First 40 chars of JSON string + `…` |

---

## Definition of done

### Phase 9 gate (automated — clearable now)
- [ ] `npx tsc --noEmit` passes with zero errors
- [ ] `npm run build` completes without errors
- [ ] Scenario 4 (blank validation) passes manually
- [ ] Scenario 6 (network error) passes manually

### Phase 10 gate (full stack — requires LocalStack)
- [ ] Scenarios 1–3 pass (tracking, events, SOP round-trips)
- [ ] Scenario 5 passes (pagination + page reset on new entry)
- [ ] No console errors in the browser during normal operation
- [ ] Audit log rows are ordered newest-first
- [ ] Pagination hides when ≤ 10 rows; shows when > 10 rows
