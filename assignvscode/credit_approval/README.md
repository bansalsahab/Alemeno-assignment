# credit_approval Backend Assignment

## Overview
A Django + DRF backend for credit approval, with background Excel ingestion, Celery, PostgreSQL, Redis, and Docker Compose. Implements all endpoints and business logic as per assignment spec.

## Quickstart
1. Clone repo and place Excel files in `/data`.
2. Build and run:  
   ```sh
   docker-compose up --build
   ```
3. The API will be available at http://localhost:8000/
4. Celery worker will ingest Excel data on startup (see logs).

## Endpoints
- `POST /register` — Register a new customer
- `POST /check-eligibility` — Check loan eligibility
- `POST /create-loan` — Create a loan
- `GET /view-loan/{loan_id}` — View a loan
- `GET /view-loans/{customer_id}` — List active loans for a customer
- `GET /health/` — Health check

## Example curl
```
curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d '{"first_name":"A","last_name":"B","age":30,"monthly_income":50000,"phone_number":"9999999999"}'
curl -X POST http://localhost:8000/check-eligibility -H "Content-Type: application/json" -d '{"customer_id":1,"loan_amount":200000,"interest_rate":10,"tenure":24}'
curl -X POST http://localhost:8000/create-loan -H "Content-Type: application/json" -d '{"customer_id":1,"loan_amount":200000,"interest_rate":10,"tenure":24}'
curl http://localhost:8000/view-loan/1
```

## Running Tests
```sh
docker-compose run web pytest
```

## Ingestion
- On container start, `python manage.py ingest_initial_data` schedules Celery tasks to ingest `/data/customer_data.xlsx` and `/data/loan_data.xlsx`.
- Check Celery logs for summary.

## Notes
- All config via `.env` file.
- OpenAPI docs: `/docs/`
- Checklist: see `CHECKLIST.md`.
- Sample responses: see `SAMPLE_RESPONSES.md`.
