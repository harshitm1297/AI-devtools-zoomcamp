# Shared Household Chores — Implementation Backlog

Each task is small enough to implement, run, and review independently.

## Task 1 — Create the household and chore data model

Create Django models for a `Household`, household membership, a weekly chore,
and a completed chore occurrence. Use Django's built-in user model for members.
Include the fields needed for an invitation code, optional chore assignee,
weekly due date, completion timestamp, and the member who completed a chore.
Register the models in Django admin, create migrations, and apply them.

**Done when:** migrations apply successfully and an administrator can create and
inspect the models in Django admin.

## Task 2 — Add invite-only household registration and sign-in

Create pages for a user to create a household, register by entering a valid
household invitation code, sign in, and sign out. Ensure only authenticated
members can access household pages.

**Done when:** a new household can be created, another user can join only with
its invitation code, and unauthenticated users are redirected to sign in.

## Task 3 — Show and create household chores

Create a household dashboard that lists active chores for the signed-in user's
household. Add a form that lets any member create a weekly chore and optionally
assign it to another member of the same household.

**Done when:** a member can create a chore and all household members can see
it, while members of another household cannot.

## Task 4 — Claim unassigned chores

Add an action for a signed-in household member to claim an unassigned chore.
Prevent users from claiming chores outside their household or chores already
assigned to someone else.

**Done when:** an unassigned chore can be claimed and the dashboard shows its
assignee.

## Task 5 — Complete weekly chores and retain history

Add an action to mark a chore complete. Record the completion in history with
the completing member and timestamp, then create the next occurrence one week
later. Add a history section to the dashboard.

**Done when:** completing a chore creates a visible history entry and leaves a
new weekly occurrence available in the active chore list.

## Task 6 — Add tests and polish the documentation

Add tests for household isolation, invitation-code registration, creating and
claiming chores, and completing a chore with its next weekly occurrence.
Update the README with local setup, test, and run instructions.

**Done when:** `uv run python manage.py test` passes and a new contributor can
run the application from the README.
