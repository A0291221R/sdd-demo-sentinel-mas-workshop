const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export interface TaskResponse {
  task_id: string;
  status: string;
  intent: string | null;
  agent_result: unknown;
  error: string | null;
}

export class NotFoundError extends Error {
  constructor() {
    super("Task not found");
    this.name = "NotFoundError";
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, init);
  if (!res.ok) {
    if (res.status === 404) throw new NotFoundError();
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status}: ${text}`);
  }
  return res.json() as Promise<T>;
}

export function postQuery(query: string): Promise<TaskResponse> {
  return request<TaskResponse>("/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
}

export function getResult(taskId: string): Promise<TaskResponse> {
  return request<TaskResponse>(`/result/${taskId}`);
}
