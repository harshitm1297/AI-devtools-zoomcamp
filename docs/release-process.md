# Release and rollback

1. Pull request runs tests, privacy guard, and container build.
2. Merge to `main` calls the development deploy hook.
3. Workflow waits for `/healthz` and smoke-tests `/version`.
4. A human reviews the development application and telemetry.
5. Production is invoked manually through the protected GitHub environment.

Rollback selects the previous immutable image tag through the hosting provider, then runs health and
assessment smoke tests. Database changes must remain backward compatible because SQLite migrations
are intentionally outside this prototype. If recovery cannot be verified, stop and escalate.

