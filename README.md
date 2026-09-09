# India Enforcement Map — MVP v1

A public-interest map of **currently open** hotels and restaurants with **verified historical enforcement actions**. Present operating status and historical events are deliberately separate. Evidence is linked to its original publisher; pending and rejected actions never qualify a public marker.

## Run locally

Requirements: Docker with Compose v2. Copy `.env.example` to `.env`, change `INTERNAL_API_KEY`, then run:

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:5174
- API docs: http://localhost:8001/docs
- Mailpit: http://localhost:8025
- Health/readiness: `GET /health`, `GET /ready`

The backend container applies Alembic migrations and inserts development data once. Seed data includes 16 establishments, 17 actions, and 22 evidence articles across Maharashtra, Delhi, Karnataka, and Rajasthan. The map still only emits establishments that are `OPEN` and have an `APPROVED` action with an article.

## Architecture

`presentation → application → domain`; infrastructure supplies PostgreSQL/PostGIS repositories, RSS adapters, AI strategies, Celery, and SMTP. Repositories flush but never commit. Use cases own transaction boundaries. Source feed URLs are database configuration, not application constants.

Celery Beat only enqueues `fetch_all_news_sources` every `NEWS_POLL_INTERVAL_MINUTES` (15 by default). A worker loads enabled sources independently, creates an adapter through `NewsSourceFactory`, polls RSS politely, normalizes and deduplicates URLs, stores only metadata/short summaries, and queues processing. One failed source is recorded and does not stop the others. The code does not bypass access controls or fetch full articles by default.

The classifier and extractor are strategy interfaces. Deterministic rules keep local development functional without model or LLM credentials; a configurable transformer strategy is available via `requirements-ml.txt` for a dedicated ML worker (kept out of the web image to avoid shipping a multi-gigabyte runtime). The LLM seam is optional and returns no result when unconfigured. AI output remains a candidate until confidence and/or review approves it.

## API

- `GET /api/v1/map/establishments` requires/accepts viewport, zoom, state, city, type, action and date filters.
- `GET /api/v1/establishments/search?q=Pune`
- `GET /api/v1/establishments/{id}`
- `GET /api/v1/reviews/{token}`
- `POST /api/v1/reviews/{token}/approve`
- `POST /api/v1/reviews/{token}/reject`
- `GET /api/v1/internal/reviews` with `X-Internal-API-Key`

Review tokens are random, SHA-256 hashed, expiring, POST-mutated, and single-use. Approval/rejection updates the review and action in one transaction.

## Tests and operational checks

```bash
docker compose run --rm backend pytest
docker compose run --rm frontend npm test
docker compose config --quiet
```

Production deployment should replace example seed evidence, use validated publisher feed URLs, terminate TLS at a reverse proxy, rotate the internal key, restrict CORS, add an API-edge rate limiter, and run the transformer as a warmed dedicated worker. RSS availability and publisher terms change; source health fields expose failures without coupling the domain to a publisher.
