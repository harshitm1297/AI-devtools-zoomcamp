import React, { useEffect, useMemo, useState } from "react";
import { api } from "./services/api";

const emptyTask = { title: "", description: "", assigneeId: "", priority: "Medium", dueDate: "", labels: "" };

function initials(member) {
  return member?.initials ?? "–";
}

function Modal({ title, onClose, children }) {
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={onClose}>
      <section className="modal" role="dialog" aria-modal="true" aria-label={title} onMouseDown={(event) => event.stopPropagation()}>
        <div className="modal-title"><h2>{title}</h2><button className="icon-button" onClick={onClose} aria-label="Close">×</button></div>
        {children}
      </section>
    </div>
  );
}

function App() {
  const [workspace, setWorkspace] = useState(null);
  const [boards, setBoards] = useState([]);
  const [board, setBoard] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [showBoardForm, setShowBoardForm] = useState(false);
  const [inviteCode, setInviteCode] = useState("");
  const [draggedTaskId, setDraggedTaskId] = useState(null);
  const [dragOverColumnId, setDragOverColumnId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const currentUser = useMemo(
    () => workspace?.members.find((member) => member.id === workspace.currentUserId),
    [workspace],
  );
  const isManager = currentUser?.role === "Project manager";

  async function loadBoard(boardId) {
    try {
      const nextBoard = await api.getBoard(boardId);
      setBoard(nextBoard);
      setSelectedTask((task) => nextBoard.tasks.find((item) => item.id === task?.id) ?? null);
    } catch (reason) {
      setError(reason.message);
    }
  }

  async function initialize() {
    try {
      const [nextWorkspace, nextBoards] = await Promise.all([api.getWorkspace(), api.listBoards()]);
      setWorkspace(nextWorkspace);
      setBoards(nextBoards);
      if (nextBoards[0]) await loadBoard(nextBoards[0].id);
    } catch (reason) {
      setError(reason.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { initialize(); }, []);

  async function refreshBoard() {
    if (!board) return;
    const [nextBoards] = await Promise.all([api.listBoards()]);
    setBoards(nextBoards);
    await loadBoard(board.id);
  }

  async function createBoard(event) {
    event.preventDefault();
    const name = new FormData(event.currentTarget).get("boardName").trim();
    if (!name) return;
    const nextBoard = await api.createBoard(name);
    setShowBoardForm(false);
    const nextBoards = await api.listBoards();
    setBoards(nextBoards);
    await loadBoard(nextBoard.id);
  }

  async function createColumn(event) {
    event.preventDefault();
    const name = new FormData(event.currentTarget).get("columnName").trim();
    if (!name || !board) return;
    await api.createColumn(board.id, name);
    event.currentTarget.reset();
    await refreshBoard();
  }

  async function createTask(event) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    const task = {
      title: fields.get("title").trim(),
      description: fields.get("description").trim(),
      assigneeId: fields.get("assigneeId") || null,
      columnId: fields.get("columnId"),
      priority: fields.get("priority"),
      dueDate: fields.get("dueDate"),
      labels: fields.get("labels").split(",").map((label) => label.trim()).filter(Boolean),
    };
    if (!task.title) return;
    await api.createTask(board.id, task);
    setShowTaskForm(false);
    await refreshBoard();
  }

  async function saveTask(event) {
    event.preventDefault();
    const fields = new FormData(event.currentTarget);
    const changes = {
      title: fields.get("title").trim(),
      description: fields.get("description").trim(),
      assigneeId: fields.get("assigneeId") || null,
      columnId: fields.get("columnId"),
      priority: fields.get("priority"),
      dueDate: fields.get("dueDate"),
      labels: fields.get("labels").split(",").map((label) => label.trim()).filter(Boolean),
    };
    await api.updateTask(board.id, selectedTask.id, changes);
    await refreshBoard();
  }

  async function addComment(event) {
    event.preventDefault();
    const field = new FormData(event.currentTarget).get("comment").trim();
    if (!field) return;
    await api.addComment(board.id, selectedTask.id, field);
    event.currentTarget.reset();
    await refreshBoard();
  }

  async function makeInvitation() {
    setInviteCode(await api.createInvitation());
  }

  async function moveTaskToColumn(taskId, columnId) {
    const task = board?.tasks.find((item) => item.id === taskId);
    if (!task || task.columnId === columnId) return;
    await api.updateTask(board.id, taskId, { columnId });
    await refreshBoard();
  }

  function startDragging(event, taskId) {
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", taskId);
    setDraggedTaskId(taskId);
  }

  async function dropTask(event, columnId) {
    event.preventDefault();
    const taskId = event.dataTransfer.getData("text/plain") || draggedTaskId;
    setDragOverColumnId(null);
    setDraggedTaskId(null);
    if (taskId) await moveTaskToColumn(taskId, columnId);
  }

  async function resetDemo() {
    await api.resetDemoData();
    setInviteCode("");
    setSelectedTask(null);
    setLoading(true);
    await initialize();
  }

  if (loading) return <main className="loading">Loading Sprintlane…</main>;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="#top"><span className="brand-mark">S</span><span>Sprintlane</span></a>
        <div className="workspace-card">
          <span className="eyebrow">Workspace</span>
          <strong>{workspace.name}</strong>
          <span className="member-count">{workspace.members.length} members</span>
        </div>
        <nav aria-label="Boards">
          <div className="section-heading"><span>Boards</span>{isManager && <button className="small-plus" onClick={() => setShowBoardForm(true)} aria-label="Create board">+</button>}</div>
          {boards.map((item) => <button key={item.id} className={`board-link ${item.id === board?.id ? "active" : ""}`} onClick={() => loadBoard(item.id)}>{item.name}</button>)}
        </nav>
        <div className="sidebar-footer">
          <div className="current-user"><span className="avatar avatar-dark">{initials(currentUser)}</span><span><strong>{currentUser?.name}</strong><small>{currentUser?.role}</small></span></div>
          <button className="text-button" onClick={resetDemo}>Reset demo data</button>
        </div>
      </aside>

      <main className="content" id="top">
        <header className="topbar">
          <div><span className="eyebrow">{workspace.name}</span><h1>{board?.name}</h1></div>
          <div className="header-actions">
            {isManager && <button className="secondary-button" onClick={makeInvitation}>Create invitation</button>}
            <button className="primary-button" onClick={() => setShowTaskForm(true)}>+ New task</button>
          </div>
        </header>

        {inviteCode && <div className="invite-banner"><span><strong>Invitation ready:</strong> share <code>{inviteCode}</code> with a teammate.</span><button className="icon-button" onClick={() => setInviteCode("")} aria-label="Dismiss invitation">×</button></div>}
        {error && <div className="error-banner">{error}</div>}
        <p className="board-hint">Drag a task card to a column to update its status.</p>

        <section className="board" aria-label={`${board?.name} Kanban board`}>
          {board?.columns.map((column) => {
            const columnTasks = board.tasks.filter((task) => task.columnId === column.id);
            return <section
              className={`column ${dragOverColumnId === column.id ? "drop-target" : ""}`}
              key={column.id}
              onDragOver={(event) => { event.preventDefault(); setDragOverColumnId(column.id); }}
              onDragLeave={() => setDragOverColumnId((current) => current === column.id ? null : current)}
              onDrop={(event) => dropTask(event, column.id)}
            >
              <div className="column-header"><h2>{column.name}</h2><span>{columnTasks.length}</span></div>
              <div className="task-list">
                {columnTasks.map((task) => <TaskCard key={task.id} task={task} workspace={workspace} onClick={() => setSelectedTask(task)} onDragStart={(event) => startDragging(event, task.id)} onDragEnd={() => { setDraggedTaskId(null); setDragOverColumnId(null); }} />)}
                {!columnTasks.length && <p className="empty-column">No tasks yet</p>}
              </div>
            </section>;
          })}
          {isManager && <form className="add-column" onSubmit={createColumn}><input name="columnName" placeholder="Custom column name" aria-label="Custom column name" /><button type="submit">Add column</button></form>}
        </section>
      </main>

      {showBoardForm && <Modal title="Create board" onClose={() => setShowBoardForm(false)}><form className="stacked-form" onSubmit={createBoard}><label>Board name<input name="boardName" autoFocus placeholder="e.g. Q4 Planning" required /></label><button className="primary-button" type="submit">Create board</button></form></Modal>}
      {showTaskForm && <Modal title="New task" onClose={() => setShowTaskForm(false)}><TaskForm board={board} workspace={workspace} values={emptyTask} onSubmit={createTask} submitLabel="Create task" /></Modal>}
      {selectedTask && <Modal title="Task details" onClose={() => setSelectedTask(null)}><TaskForm board={board} workspace={workspace} values={{ ...selectedTask, labels: selectedTask.labels.join(", ") }} onSubmit={saveTask} submitLabel="Save changes" /><section className="comments"><h3>Comments</h3>{selectedTask.comments.map((comment) => <Comment key={comment.id} comment={comment} workspace={workspace} />)}{!selectedTask.comments.length && <p className="muted">No comments yet.</p>}<form className="comment-form" onSubmit={addComment}><textarea name="comment" placeholder="Add an update or question…" required /><button className="secondary-button" type="submit">Comment</button></form></section></Modal>}
    </div>
  );
}

function TaskCard({ task, workspace, onClick, onDragStart, onDragEnd }) {
  const assignee = workspace.members.find((member) => member.id === task.assigneeId);
  return <button className="task-card" draggable="true" onClick={onClick} onDragStart={onDragStart} onDragEnd={onDragEnd}>
    <div className="task-card-top"><span className={`priority priority-${task.priority.toLowerCase()}`}>{task.priority}</span>{task.dueDate && <span className="due-date">{task.dueDate.slice(5)}</span>}</div>
    <strong>{task.title}</strong>
    <div className="labels">{task.labels.map((label) => <span key={label}>{label}</span>)}</div>
    <div className="task-card-footer"><span className="comment-count">◌ {task.comments.length}</span>{assignee ? <span className="avatar" title={assignee.name}>{initials(assignee)}</span> : <span className="unassigned">Unassigned</span>}</div>
  </button>;
}

function TaskForm({ board, workspace, values, onSubmit, submitLabel }) {
  return <form className="stacked-form task-form" onSubmit={onSubmit}>
    <label>Title<input name="title" defaultValue={values.title} required /></label>
    <label>Description<textarea name="description" defaultValue={values.description} rows="3" /></label>
    <div className="form-grid"><label>Column<select name="columnId" defaultValue={values.columnId || board.columns[0]?.id}>{board.columns.map((column) => <option key={column.id} value={column.id}>{column.name}</option>)}</select></label><label>Priority<select name="priority" defaultValue={values.priority}>{["Low", "Medium", "High"].map((priority) => <option key={priority}>{priority}</option>)}</select></label></div>
    <div className="form-grid"><label>Assignee<select name="assigneeId" defaultValue={values.assigneeId || ""}><option value="">Unassigned</option>{workspace.members.map((member) => <option key={member.id} value={member.id}>{member.name}</option>)}</select></label><label>Due date<input name="dueDate" type="date" defaultValue={values.dueDate} /></label></div>
    <label>Labels <small>Comma-separated</small><input name="labels" defaultValue={values.labels} placeholder="Design, Planning" /></label>
    <button className="primary-button" type="submit">{submitLabel}</button>
  </form>;
}

function Comment({ comment, workspace }) {
  const author = workspace.members.find((member) => member.id === comment.authorId);
  return <article className="comment"><span className="avatar">{initials(author)}</span><div><strong>{author?.name}</strong><time>{comment.createdAt}</time><p>{comment.body}</p></div></article>;
}

export default App;
