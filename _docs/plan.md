# Shared Household Chores — MVP Plan

## Product goal

Build a small web application that helps equal housemates coordinate shared
household chores. Everyone in a household can see the same chore list, take
responsibility for unassigned chores, and see what has been completed.

## Target users

Equal housemates who share a household and want a lightweight, shared place to
manage recurring weekly chores.

## Core features

1. **Invite-only households and accounts**
   - A user can create a household and becomes its initial member.
   - The household has an invitation code that a new user can enter when
     registering, so only invited people can join.
   - Members sign in to access their household's chores.

2. **Shared household chore list**
   - Any household member can create a chore with a title and a weekly schedule.
   - Members see only chores belonging to their own household.

3. **Assigned and self-claimed chores**
   - When creating a chore, a member may assign it to a housemate or leave it
     unassigned.
   - Any household member can claim an unassigned chore.

4. **Completion, recurrence, and history**
   - A member can mark a chore as complete.
   - The completed occurrence is retained in the household's history, including
     who completed it and when.
   - Completing a weekly chore creates its next weekly occurrence.

## Main user flow

1. A housemate creates a household and receives an invitation code.
2. Other housemates register with that code and join the same household.
3. Members add chores, optionally assigning them to a member.
4. A member claims an unassigned chore or completes an assigned chore.
5. The app records the completion and creates the next weekly occurrence.

## Out of scope for this homework

- Notifications, reminders, email invitations, or push alerts.
- Fairness scoring, chore rotation, points, or leaderboards.
- Different recurrence patterns beyond weekly.
- Editing or deleting chores after creation.
- Multiple households per user, administrator roles, or payments.
- A JavaScript frontend or public API; Django-rendered pages are sufficient.

## Success criteria

A signed-in household member can add a weekly chore, assign it or leave it
unassigned, claim an unassigned chore, mark it complete, and see both its
completion record and its next weekly occurrence.
