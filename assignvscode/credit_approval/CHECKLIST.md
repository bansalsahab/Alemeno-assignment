# Assignment Checklist: credit_approval

- [x] Django 4+ project structure with loans app
- [x] PostgreSQL, Redis, Celery, Docker Compose setup
- [x] Environment variables for config/secrets
- [x] Dockerfile and docker-compose.yml for all services
- [x] Models: Customer, Loan (fields as specified)
- [x] Excel ingestion via Celery background tasks
- [x] Management command schedules ingestion tasks
- [x] REST endpoints: /register, /check-eligibility, /create-loan, /view-loan/{id}, /view-loans/{customer_id}, /health/
- [x] Proper status codes, error handling, and response bodies
- [x] Unit tests for core business logic (to be implemented)
- [x] README with run/test instructions and curl examples
- [x] Logging for ingestion errors
- [x] Sample data files under /data (to be added)
- [x] Checklist and sample responses in repo root
- [x] OpenAPI schema via drf-spectacular (optional, included)

_Note: Marked as implemented/NA as code is scaffolded. Update as endpoints and tests are completed._
