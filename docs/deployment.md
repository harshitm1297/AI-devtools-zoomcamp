# Deployment

The application is one container with a persistent `/data` volume. Configure `AI_MODE=demo` for the
fixed sample, `AI_MODE=ollama` with an accessible local Ollama server for free receipt reading, or
`AI_MODE=openai` with a platform-managed `OPENAI_API_KEY`. Never bake a key into an image.

For Ollama, pull `gemma3:4b` before starting the app and set `OLLAMA_BASE_URL` to the server address.
The Compose default is `http://host.docker.internal:11434`.

Required platform settings:

```text
port: 8000
health check: /healthz
persistent volume: /data
DATABASE_PATH: /data/guardian_angel.db
APP_VERSION: immutable image tag or commit SHA
```

GitHub Actions expects these repository settings:

- `DEV_DEPLOY_HOOK_URL` and `DEV_BASE_URL` for automatic development deployment.
- `PROD_DEPLOY_HOOK_URL` and `PROD_BASE_URL` in a protected `production` environment.

The deploy hook must deploy the immutable image built for that commit. A platform-specific adapter
may be substituted when a hosting provider is selected.

