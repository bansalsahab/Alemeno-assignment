
# Alemeno Credit Approval Backend

This project is a Django REST Framework (DRF) backend for a credit approval system, designed for the Alemeno assignment. It features background Excel ingestion, asynchronous task processing with Celery, PostgreSQL for data storage, Redis for task brokering, and full Docker Compose orchestration.

## Features

- **Customer Registration** and management
- **Loan Eligibility** checks and loan creation
- **Excel Data Ingestion** (customers and loans) via Celery tasks
- **API-first**: All endpoints documented and testable
- **Dockerized**: One-command setup for local development
- **OpenAPI docs**: Interactive API documentation at `/docs/`

## Tech Stack

- Python 3.11, Django 4.x, Django REST Framework
- Celery 5.x, Redis 7.x
- PostgreSQL 15
- Docker, Docker Compose
- pandas, openpyxl (for Excel ingestion)

## Quickstart

1. **Clone the repository**
   ```sh
   git clone https://github.com/bansalsahab/Alemeno-assignment.git
   cd Alemeno-assignment/credit_approval
   ```
2. **Add Excel Data**
   - Place `customer_data.xlsx` and `loan_data.xlsx` in the `../data/` directory (relative to `credit_approval`).
3. **Configure Environment**
   - Copy `.env.example` to `.env` and update as needed (DB credentials, etc).
4. **Build and Run**
   ```sh
   docker-compose up --build
   ```
5. **Access the API**
   - API root: [http://localhost:8000/](http://localhost:8000/)
   - Docs: [http://localhost:8000/docs/](http://localhost:8000/docs/)

## API Endpoints

| Method | Endpoint                  | Description                        |
|--------|---------------------------|------------------------------------|
| POST   | `/register`               | Register a new customer            |
| POST   | `/check-eligibility`      | Check loan eligibility             |
| POST   | `/create-loan`            | Create a new loan                  |
| GET    | `/view-loan/{loan_id}`    | View details of a specific loan    |
| GET    | `/view-loans/{customer_id}` | List all active loans for customer |
| GET    | `/health/`                | Health check endpoint              |

### Example Requests

```sh
# Register a customer
curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d '{"first_name":"A","last_name":"B","age":30,"monthly_income":50000,"phone_number":"9999999999"}'

# Check eligibility
curl -X POST http://localhost:8000/check-eligibility -H "Content-Type: application/json" -d '{"customer_id":1,"loan_amount":200000,"interest_rate":10,"tenure":24}'

# Create a loan
curl -X POST http://localhost:8000/create-loan -H "Content-Type: application/json" -d '{"customer_id":1,"loan_amount":200000,"interest_rate":10,"tenure":24}'

# View a loan
curl http://localhost:8000/view-loan/1
```

## Data Ingestion

- On container startup, Celery tasks ingest data from `/data/customer_data.xlsx` and `/data/loan_data.xlsx`.
- Ingestion is scheduled via `python manage.py ingest_initial_data`.
- Check Celery logs for ingestion status and errors.

## Running Tests

```sh
docker-compose run web pytest
```

## Project Structure

```
credit_approval/
├── app/
│   ├── credit_approval/   # Django project
│   └── loans/             # Loans app (models, views, tasks)
├── data/                  # Place Excel files here
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── start.sh
├── CHECKLIST.md           # Assignment checklist
├── SAMPLE_RESPONSES.md    # Example API responses
└── README.md
```

## Configuration

- All environment variables are managed via `.env`.
- Database, Redis, and other service credentials can be set there.

## Documentation & References

- **OpenAPI docs**: `/docs/`
- **Assignment checklist**: `CHECKLIST.md`
- **Sample responses**: `SAMPLE_RESPONSES.md`

## License

This project is for educational/assignment use. See assignment instructions for details.
