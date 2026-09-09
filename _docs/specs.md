# Sprintlane — Product Specification

## Product summary

Sprintlane is a lightweight, invite-only Kanban board for a project manager and
their team. It helps the team organize work, assign tasks, discuss progress,
and move work through a visible workflow.

## Users and roles

### Project manager

- Creates a team workspace and boards.
- Generates and shares invitation links or codes for team members.
- Creates boards with the default workflow and may add custom columns.

### Team member

- Joins a workspace only through a manager-created invitation.
- Can view the workspace's boards.
- Can create and edit tasks, move tasks between columns, and add comments.

## Core features

### 1. Invite-only accounts and workspaces

- Users sign in with an email address and password.
- A project manager creates a workspace and can create an invitation for a team
  member.
- A user may join a workspace only with a valid invitation.
- Users may access only the workspaces and boards they belong to.

### 2. Boards and workflow columns

- A project manager can create a board.
- Every new board starts with four ordered columns: **Backlog**, **To Do**,
  **In Progress**, and **Done**.
- The project manager can add custom columns to a board.
- A task's status is the column in which it currently appears.

### 3. Shared task management

- Any workspace member can create and edit a task.
- A task has a title, description, assignee, column/status, priority, optional
  due date, and zero or more labels.
- Members can move a task from one column to another.
- Members can assign tasks only to people in the same workspace.

### 4. Task comments

- Any workspace member can add a text comment to a task.
- Each comment displays its author and creation time.
- Members can see comments for tasks on boards in their workspace.

## Main user flows

### Create and populate a board

1. A project manager signs up and creates a workspace.
2. The manager creates a board; Sprintlane creates the four default columns.
3. The manager creates an invitation and shares it with a teammate.
4. The teammate registers through that invitation and joins the workspace.
5. Either member creates a task, assigns it, and places it in a column.

### Work on a task

1. A team member opens a board in their workspace.
2. They create or edit a task, including its priority, due date, labels, and
   assignee.
3. They move the task to a new column as its status changes.
4. A teammate adds a comment to record context or an update.

## Acceptance criteria

- An unauthenticated user cannot view a workspace or board.
- A user without a valid invitation cannot join a workspace.
- A new board contains Backlog, To Do, In Progress, and Done in that order.
- Only the project manager can add a custom column.
- Any workspace member can create, edit, assign, and move a task.
- A task never appears on a board outside its workspace.
- A task can be assigned only to a workspace member.
- A comment records its author and timestamp and is visible on its task.
- Task, column, comment, and membership data still exists after the backend is
  restarted.

## Non-goals for this homework

- Email delivery, notifications, reminders, and @mentions.
- Real-time updates, drag-and-drop interaction, attachments, and file uploads.
- Task deletion, audit logs, reporting, search, filters, and analytics.
- Multiple manager roles, billing, public boards, or external integrations.
- Mobile applications.

## Technical direction

- Frontend: an interactive web application with a centralized mocked service
  layer before the real API is connected.
- Backend: FastAPI implementing an OpenAPI contract.
- Persistence: SQLAlchemy with SQLite, configured by an environment variable
  and designed so PostgreSQL can replace SQLite later.
