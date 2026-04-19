# Plan — Phase 9: React Operator Dashboard

_Branch: `phase-9-react-operator-dashboard` | Date: 2026-04-19_

---

## Task groups

Groups are independently completable in order. Each group can be reviewed and
tested before the next begins.

---

### Group 1 — Scaffold

1.1 Create `services/ui/` via Vite:
    ```
    npm create vite@latest ui -- --template react-ts
    ```
    Run from `services/` so the app lands at `services/ui/`.

1.2 Remove boilerplate files: `src/App.css`, `src/assets/`, placeholder
    content in `src/App.tsx` and `index.css`.

1.3 Add `VITE_API_URL` to `services/ui/.env.local` (default
    `http://localhost:8000`). Add `.env.local` to `.gitignore`.

1.4 Verify `npm run dev` starts without errors and the Vite default page
    renders in the browser.

---

### Group 2 — API client module

2.1 Create `src/api.ts` exporting:
    - `postQuery(query: string): Promise<TaskResponse>` — POST /query
    - `getResult(taskId: string): Promise<TaskResponse>` — GET /result/{task_id}
    - `TaskResponse` TypeScript interface matching the API shape:
      ```ts
      interface TaskResponse {
        task_id: string;
        status: string;
        intent: string | null;
        agent_result: unknown;
        error: string | null;
      }
      ```

2.2 Read `VITE_API_URL` from `import.meta.env.VITE_API_URL` with fallback
    to `"http://localhost:8000"`.

2.3 Both functions throw on non-2xx responses, passing through the response
    body as the error message where available.

---

### Group 3 — QueryForm component

3.1 Create `src/components/QueryForm.tsx`:
    - Controlled `<input>` bound to local state
    - `<button>` disabled when `loading === true` or input is blank/whitespace
    - Client-side validation: if user submits blank query, show inline
      `"Query cannot be empty"` error without calling the API
    - On valid submit: call `onSubmit(query: string)` prop

3.2 Props interface:
    ```ts
    interface QueryFormProps {
      onSubmit: (query: string) => void;
      loading: boolean;
    }
    ```

---

### Group 4 — ResultPanel component

4.1 Create `src/components/ResultPanel.tsx`:
    - Renders `status`, `intent`, and `agent_result` (JSON.stringify with
      2-space indent inside a `<pre>` block)
    - Shows a spinner (`"Loading…"` text) when `status === "pending"`
    - Shows `error` field in red if present
    - Renders nothing (or a placeholder) when no task has been submitted yet

4.2 Props interface:
    ```ts
    interface ResultPanelProps {
      task: TaskResponse | null;
      loading: boolean;
    }
    ```

---

### Group 5 — AuditLogTable component

5.1 Create `src/components/AuditLogTable.tsx`:
    - Columns: Task ID (first 8 chars + `…`), Intent, Status,
      Agent Result (first 40 chars of JSON.stringify, truncated with `…`)
    - Rows ordered newest-first
    - Pagination: 10 rows per page; Previous / Next buttons; hide if ≤ 10 rows

5.2 Props interface:
    ```ts
    interface AuditLogTableProps {
      rows: TaskResponse[];
    }
    ```

---

### Group 6 — App assembly and polling logic

6.1 Update `src/App.tsx`:
    - State: `task: TaskResponse | null`, `loading: boolean`,
      `error: string | null`, `auditLog: TaskResponse[]`
    - `handleSubmit(query)`:
      1. Set `loading = true`, clear `error`
      2. Call `postQuery(query)` → get initial `TaskResponse`
      3. Set `task` to the pending response
      4. Start polling: `setInterval` calling `getResult(task_id)` every 1 000 ms
      5. On each poll: update `task`; if `status !== "pending"`, clear interval,
         set `loading = false`, append task to `auditLog`
      6. On network error: clear interval, set `loading = false`, set `error`
    - Render: `<QueryForm>`, `<ResultPanel>`, `<AuditLogTable>`

6.2 Clean up the polling interval in a `useEffect` cleanup function to avoid
    stale-closure leaks on unmount.

---

### Group 7 — Styling

7.1 Add minimal CSS in `src/index.css`:
    - Page max-width 900px, centred
    - Section headings for result panel and audit log
    - Table with `border-collapse`, alternating row shading
    - Spinner: CSS animation on a `<span>` (or `"Loading…"` text if minimal)
    - Error text in red (`color: #c0392b`)

7.2 No external CSS library — plain CSS only.

---

### Group 8 — Integration smoke test

8.1 Start the FastAPI service: `uvicorn services.api.main:app --reload`.

8.2 Start the Vite dev server: `npm run dev` (from `services/ui/`).

8.3 Submit a tracking query and verify the result panel updates from
    `pending` → `completed` and the audit log row appears.

8.4 Submit a blank query and verify the inline validation error appears
    without a network request.

8.5 Confirm pagination: submit > 10 queries and verify Previous / Next work.

_(Full walkthrough in `validation.md`.)_
