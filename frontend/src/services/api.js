// The only frontend-to-backend boundary. Its method names deliberately match
// the original mock service so UI components remain unaware of transport.

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8091";
let accessToken;

async function login() {
  const response = await fetch(`${API_BASE_URL}/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "maya@example.com", password: "demo-password" }),
  });
  if (!response.ok) throw new Error("Could not start the Sprintlane demo session.");
  ({ accessToken } = await response.json());
}

async function request(path, options = {}) {
  if (!accessToken) await login();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      Authorization: `Bearer ${accessToken}`,
      ...(options.body ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail ?? "The backend request failed.");
  }
  return response.json();
}

function taskPayload(values) {
  const payload = { ...values };
  if ("dueDate" in payload) payload.dueDate = payload.dueDate || null;
  return payload;
}

function normalizeTask(task) {
  return { ...task, dueDate: task.dueDate ?? "" };
}

function normalizeBoard(board) {
  return { ...board, tasks: board.tasks?.map(normalizeTask) ?? [] };
}

export const api = {
  getWorkspace: () => request("/v1/workspace"),
  listBoards: () => request("/v1/boards"),
  getBoard: async (boardId) => normalizeBoard(await request(`/v1/boards/${boardId}`)),
  createBoard: async (name) => normalizeBoard(await request("/v1/boards", { method: "POST", body: JSON.stringify({ name }) })),
  createColumn: (boardId, name) => request(`/v1/boards/${boardId}/columns`, { method: "POST", body: JSON.stringify({ name }) }),
  createTask: async (boardId, values) => normalizeTask(await request(`/v1/boards/${boardId}/tasks`, { method: "POST", body: JSON.stringify(taskPayload(values)) })),
  updateTask: async (boardId, taskId, changes) => normalizeTask(await request(`/v1/boards/${boardId}/tasks/${taskId}`, { method: "PATCH", body: JSON.stringify(taskPayload(changes)) })),
  addComment: (boardId, taskId, body) => request(`/v1/boards/${boardId}/tasks/${taskId}/comments`, { method: "POST", body: JSON.stringify({ body }) }),
  createInvitation: async () => (await request("/v1/invitations", { method: "POST" })).code,
  resetDemoData: () => request("/v1/demo/reset", { method: "POST" }),
};
