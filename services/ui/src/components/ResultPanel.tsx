import type { TaskResponse } from "../api";

interface ResultPanelProps {
  task: TaskResponse | null;
  loading: boolean;
}

export default function ResultPanel({ task, loading }: ResultPanelProps) {
  if (task === null) {
    return <p className="placeholder">No query submitted yet.</p>;
  }

  return (
    <div className="result-panel">
      <p>
        <strong>Status:</strong> {task.status}
        {task.intent ? <> &nbsp;|&nbsp; <strong>Intent:</strong> {task.intent}</> : null}
      </p>
      {loading && <p className="spinner">Loading…</p>}
      {task.error && <p className="error-text">Error: {task.error}</p>}
      {task.agent_result !== null && task.agent_result !== undefined && (
        <>
          <strong>Result:</strong>
          <pre className="result-pre">
            {JSON.stringify(task.agent_result, null, 2)}
          </pre>
        </>
      )}
    </div>
  );
}
