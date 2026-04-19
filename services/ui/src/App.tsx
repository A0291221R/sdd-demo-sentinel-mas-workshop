import { useState } from "react";
import type { TaskResponse } from "./api";
import AuditLogTable from "./components/AuditLogTable";
import QueryForm from "./components/QueryForm";
import ResultPanel from "./components/ResultPanel";
import { useTaskPoller } from "./hooks/useTaskPoller";

export default function App() {
  const [auditLog, setAuditLog] = useState<TaskResponse[]>([]);
  const { task, loading, error, clearError, submit } = useTaskPoller();

  function handleSubmit(query: string) {
    submit(query, (resolved) => {
      setAuditLog((prev) => [resolved, ...prev]);
    });
  }

  return (
    <div className="app">
      <h1>Sentinel MAS — Operator Dashboard</h1>

      <section className="section">
        <QueryForm onSubmit={handleSubmit} onClearError={clearError} loading={loading} />
        {error && <p className="error-text">{error}</p>}
      </section>

      <section className="section">
        <h2>Result</h2>
        <ResultPanel task={task} loading={loading} />
      </section>

      <section className="section">
        <h2>Audit Log</h2>
        <AuditLogTable rows={auditLog} />
      </section>
    </div>
  );
}
