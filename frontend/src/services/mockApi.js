// This module is the frontend's single integration boundary. Replace these
// functions with HTTP calls once the FastAPI backend and openapi.yaml exist.

const STORAGE_KEY = "sprintlane-mock-data-v1";
const wait = (value) => new Promise((resolve) => setTimeout(() => resolve(value), 120));
const copy = (value) => structuredClone(value);
const id = (prefix) => `${prefix}-${crypto.randomUUID()}`;

const initialData = {
  workspace: {
    id: "workspace-1",
    name: "Northstar Product",
    currentUserId: "user-1",
    members: [
      { id: "user-1", name: "Maya Chen", initials: "MC", role: "Project manager" },
      { id: "user-2", name: "Jordan Lee", initials: "JL", role: "Team member" },
      { id: "user-3", name: "Avery Patel", initials: "AP", role: "Team member" },
    ],
  },
  boards: [
    {
      id: "board-1",
      name: "Sprint 12",
      columns: [
        { id: "column-backlog", name: "Backlog" },
        { id: "column-todo", name: "To Do" },
        { id: "column-progress", name: "In Progress" },
        { id: "column-done", name: "Done" },
      ],
      tasks: [
        {
          id: "task-1",
          title: "Outline onboarding flow",
          description: "Capture the first-time user path and review it with the team.",
          assigneeId: "user-2",
          columnId: "column-progress",
          priority: "High",
          dueDate: "2026-09-12",
          labels: ["Design", "Onboarding"],
          comments: [
            { id: "comment-1", authorId: "user-1", body: "Please include the invitation step.", createdAt: "Today, 09:20" },
          ],
        },
        {
          id: "task-2",
          title: "Confirm API fields",
          description: "List the fields the frontend needs for a task card.",
          assigneeId: "user-3",
          columnId: "column-todo",
          priority: "Medium",
          dueDate: "2026-09-14",
          labels: ["Backend"],
          comments: [],
        },
        {
          id: "task-3",
          title: "Create project brief",
          description: "Write a concise brief for the next sprint.",
          assigneeId: null,
          columnId: "column-backlog",
          priority: "Low",
          dueDate: "",
          labels: ["Planning"],
          comments: [],
        },
      ],
    },
  ],
};

function readData() {
  const saved = localStorage.getItem(STORAGE_KEY);
  return saved ? JSON.parse(saved) : copy(initialData);
}

function writeData(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

function findBoard(data, boardId) {
  const board = data.boards.find((item) => item.id === boardId);
  if (!board) throw new Error("Board not found");
  return board;
}

export const mockApi = {
  getWorkspace: async () => wait(copy(readData().workspace)),
  listBoards: async () => wait(copy(readData().boards.map(({ tasks, ...board }) => board))),
  getBoard: async (boardId) => wait(copy(findBoard(readData(), boardId))),

  createBoard: async (name) => {
    const data = readData();
    const board = {
      id: id("board"),
      name,
      columns: ["Backlog", "To Do", "In Progress", "Done"].map((columnName) => ({
        id: id("column"),
        name: columnName,
      })),
      tasks: [],
    };
    data.boards.push(board);
    writeData(data);
    return wait(copy(board));
  },

  createColumn: async (boardId, name) => {
    const data = readData();
    const board = findBoard(data, boardId);
    const column = { id: id("column"), name };
    board.columns.push(column);
    writeData(data);
    return wait(copy(column));
  },

  createTask: async (boardId, values) => {
    const data = readData();
    const board = findBoard(data, boardId);
    const task = { id: id("task"), comments: [], ...values };
    board.tasks.push(task);
    writeData(data);
    return wait(copy(task));
  },

  updateTask: async (boardId, taskId, changes) => {
    const data = readData();
    const task = findBoard(data, boardId).tasks.find((item) => item.id === taskId);
    if (!task) throw new Error("Task not found");
    Object.assign(task, changes);
    writeData(data);
    return wait(copy(task));
  },

  addComment: async (boardId, taskId, body) => {
    const data = readData();
    const board = findBoard(data, boardId);
    const task = board.tasks.find((item) => item.id === taskId);
    if (!task) throw new Error("Task not found");
    const comment = {
      id: id("comment"),
      authorId: data.workspace.currentUserId,
      body,
      createdAt: "Just now",
    };
    task.comments.push(comment);
    writeData(data);
    return wait(copy(comment));
  },

  createInvitation: async () => wait(`SPRINT-${Math.random().toString(36).slice(2, 8).toUpperCase()}`),
  resetDemoData: async () => {
    localStorage.removeItem(STORAGE_KEY);
    return wait(copy(initialData));
  },
};
