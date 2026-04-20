import { useState } from "react";
import type { TaskResponse } from "../api";

const PAGE_SIZE = 10;

function truncate(s: string, max: number): string {
  return s.length > max ? s.slice(0, max) + "…" : s;
}

interface AuditLogTableProps {
  rows: TaskResponse[];
}

export default function AuditLogTable({ rows }: AuditLogTableProps) {
  const [page, setPage] = useState(0);
  const totalPages = Math.ceil(rows.length / PAGE_SIZE);
  const safePage = Math.min(page, Math.max(0, totalPages - 1));

  if (rows.length === 0) {
    return <p className="placeholder">No completed queries yet.</p>;
  }

  const slice = rows.slice(safePage * PAGE_SIZE, (safePage + 1) * PAGE_SIZE);

  return (
    <div className="audit-log">
      <table className="audit-table">
        <thead>
          <tr>
            <th>Task ID</th>
            <th>Intent</th>
            <th>Status</th>
            <th>Agent Result</th>
          </tr>
        </thead>
        <tbody>
          {slice.map((row) => (
            <tr key={row.task_id}>
              <td>{truncate(row.task_id, 8)}</td>
              <td>{row.intent ?? "—"}</td>
              <td>{row.status}</td>
              <td>{truncate(JSON.stringify(row.agent_result), 40)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => setPage((p) => p - 1)} disabled={safePage === 0}>
            Previous
          </button>
          <span>
            {safePage + 1} / {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => p + 1)}
            disabled={safePage >= totalPages - 1}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
