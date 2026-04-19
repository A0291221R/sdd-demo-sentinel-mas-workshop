import { useEffect, useRef, useState } from "react";
import { getResult, postQuery, NotFoundError } from "../api";
import type { TaskResponse } from "../api";

const POLL_INTERVAL_MS = 1000;

export function useTaskPoller() {
  const [task, setTask] = useState<TaskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const generationRef = useRef(0);

  function clearPolling() {
    if (intervalRef.current !== null) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }

  useEffect(() => () => clearPolling(), []);

  async function submit(
    query: string,
    onResolved: (task: TaskResponse) => void,
  ) {
    clearPolling();
    const gen = ++generationRef.current;
    setLoading(true);
    setError(null);

    let initial: TaskResponse;
    try {
      initial = await postQuery(query);
    } catch (err) {
      if (gen !== generationRef.current) return;
      setError(`Network error: ${String(err)}`);
      setLoading(false);
      return;
    }

    if (gen !== generationRef.current) return;
    setTask(initial);

    if (initial.status !== "pending") {
      setLoading(false);
      onResolved(initial);
      return;
    }

    intervalRef.current = setInterval(async () => {
      try {
        const updated = await getResult(initial.task_id);
        if (gen !== generationRef.current) return;
        setTask(updated);
        if (updated.status !== "pending") {
          clearPolling();
          setLoading(false);
          onResolved(updated);
        }
      } catch (err) {
        if (gen !== generationRef.current) return;
        clearPolling();
        setError(
          err instanceof NotFoundError
            ? "Task not found"
            : `Network error: ${String(err)}`,
        );
        setLoading(false);
      }
    }, POLL_INTERVAL_MS);
  }

  return { task, loading, error, clearError: () => setError(null), submit };
}
