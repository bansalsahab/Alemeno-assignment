You are building a complete Django + Django REST Framework backend application called **credit_approval** for a Backend internship assignment. Follow the requirements exactly as specified in the assignment document (see attached). Key details: use Django 4+, PostgreSQL, Dockerized stack, background workers to ingest provided Excel files, implement specific REST endpoints with exact response bodies and logic. The provided data files are:

- /data/customer_data.xlsx
- /data/loan_data.xlsx

Use Celery + Redis for background tasks. Use pandas + openpyxl for XLSX ingestion.

--- Project goals & constraints
1. Code must be production-like, clean, well-organized, and modular.
2. Single docker-compose up should start all services (web, db, redis, celery worker, celery beat optional).
3. Use environment variables for secrets/config.
4. Provide clear README with run & test steps and required curl examples.
5. Implement all APIs with proper status codes and error handling as specified in the assignment PDF. Unit tests for core business logic are required (bonus if many tests).
6. Implement the Excel ingestion using background tasks (Celery): on container start a management command should schedule Celery tasks to ingest the two files.
7. Provide sample data fixtures (or use the given files) under /data for local dev.

--- Tech & libs
- Python 3.11+ (or 3.10)
- Django 4.x, djangorestframework
- psycopg2-binary
- celery
- redis
- pandas, openpyxl
- python-dotenv
- gunicorn (for production container)
- pytest + pytest-django or Django TestCase (for unit tests)

--- Repo layout (exact)
credit_approval/
├─ app/                       # main Django app (or project "credit_approval" + app "loans")
│  ├─ credit_approval/        # Django project settings
│  ├─ loans/                  # app implementing models, views, serializers, tasks
│  │  ├─ models.py
│  │  ├─ serializers.py
│  │  ├─ views.py
│  │  ├─ urls.py
│  │  ├─ tasks.py             # Celery tasks
│  │  ├─ management/commands/
│  │  │   └─ ingest_initial_data.py
│  │  └─ tests/
│  └─ ...
├─ Dockerfile
├─ docker-compose.yml
├─ requirements.txt
├─ data/
│  ├─ customer_data.xlsx
│  └─ loan_data.xlsx
├─ README.md

--- Models (explicit fields)
Customer
- id: AutoField (customer_id)
- first_name: CharField
- last_name: CharField
- phone_number: CharField (store as string to allow leading zeros)
- age: IntegerField (nullable if not provided)
- monthly_income: DecimalField (max_digits=12, decimal_places=2)
- approved_limit: DecimalField (max_digits=12, decimal_places=2)
- current_debt: DecimalField (default 0.00)
- created_at, updated_at timestamps

Loan
- id: AutoField (loan_id)
- customer: ForeignKey(Customer, related_name='loans')
- loan_amount: DecimalField
- tenure_months: IntegerField
- annual_interest_rate: DecimalField (e.g., 12.5)
- monthly_repayment: DecimalField
- emis_paid_on_time: IntegerField (count of EMIs paid on time from the XLSX)
- start_date: DateField
- end_date: DateField (computed)
- is_active: BooleanField
- repayments_left: IntegerField (computed)
- created_at, updated_at

--- Excel ingestion (background)
Implement a management command `ingest_initial_data` that when executed schedules two Celery tasks:
- `tasks.load_customers_from_excel(path='/data/customer_data.xlsx')`
- `tasks.load_loans_from_excel(path='/data/loan_data.xlsx')`

Tasks should:
- Parse the Excel using pandas.read_excel(..., engine='openpyxl').
- Validate rows and create/update Customer and Loan rows using bulk_create/bulk_update inside atomic transactions.
- Compute `approved_limit` for customers where missing: approved_limit = 36 * monthly_salary then **round to nearest lakh** (nearest 100,000). Use Python: `round(value / 100000) * 100000`.
- For loans, compute monthly_repayment using standard EMI formula (compound interest/annuity formula) described below.
- Log any row parsing errors; return a summary dict (created_count, updated_count, errors).

--- EMI (monthly_installment) formula (explicit)
Given principal P, annual rate R (percent), tenure in months N:
- i = (R / 100) / 12  # monthly rate
- EMI = P * i * (1+i)**N / ((1+i)**N - 1)
Implement in decimal with rounding to 2 decimal places. If R == 0 then EMI = P / N.

--- Endpoint specifications (implement exactly)

1) POST /register
- Purpose: Add a new customer and compute approved_limit
- Request body (JSON):
  {
    "first_name": "string",
    "last_name": "string",
    "age": int,
    "monthly_income": number,
    "phone_number": "string or int"
  }
- Behavior:
  - approved_limit = 36 * monthly_income, rounded to nearest lakh (100000).
  - Save customer and return 201 Created.
- Response body (201):
  {
    "customer_id": int,
    "name": "First Last",
    "age": int,
    "monthly_income": number,
    "approved_limit": number,
    "phone_number": "string"
  }

2) POST /check-eligibility
- Request body:
  {
    "customer_id": int,
    "loan_amount": float,
    "interest_rate": float,
    "tenure": int   # months
  }
- Business logic summary (exact rules from assignment, implement as follows):
  - If sum of current active loan amounts for customer > customer.approved_limit => credit_score = 0.
  - If sum of all current EMIs > 50% of monthly salary => automatically not approved (return approval=false).
  - Compute credit_score (0-100) from historical loan data using this deterministic scoring algorithm:
      * on_time_ratio = total_emis_paid_on_time / total_emis_count  (0..1)
      * score_on_time = on_time_ratio * 50
      * loans_count_penalty = max(0, 20 - number_of_past_loans) mapping (we will use: more loans => slightly lower score):
          score_loans = max(0, 20 - min(number_of_past_loans, 20))
      * current_year_activity_bonus = min(10, number_of_loans_started_this_year * 2)
      * loan_volume_factor = min(20, approved_volume_score) where approved_volume_score = max(0, 20 - (sum_past_loan_amounts / (monthly_income*12)) )  # this is a heuristic
      * credit_score = round(score_on_time + score_loans + current_year_activity_bonus + loan_volume_factor)
  - If sum of current loans > approved_limit => set credit_score = 0.
  - Based on credit_score, approval decision:
      * If credit_score > 50: APPROVE any interest rate.
      * If 30 < credit_score <= 50: only approve if interest_rate > 12%
      * If 10 < credit_score <= 30: only approve if interest_rate > 16%
      * If credit_score <= 10: DO NOT approve any loans.
  - If requested interest_rate < slab_minimum_rate for the slab, set corrected_interest_rate = slab_minimum_rate (use slab minimum: 0 for >50, 12 for 30-50, 16 for 10-30). Include corrected_interest_rate in response (if no correction, return same as interest_rate).
  - monthly_installment = EMI computed using the formula above.
- Response body (200):
  {
    "customer_id": int,
    "approval": boolean,
    "interest_rate": float,
    "corrected_interest_rate": float,
    "tenure": int,
    "monthly_installment": float,
    "credit_score": int
  }
- Use status 400 for invalid inputs, 404 if customer not found.

3) POST /create-loan
- Request body:
  {
    "customer_id": int,
    "loan_amount": float,
    "interest_rate": float,
    "tenure": int
  }
- Behavior:
  - Re-run check-eligibility logic. If approved, create Loan model with:
      - loan_amount, annual_interest_rate (corrected_interest_rate if corrected), monthly_repayment, start_date = today, end_date computed based on tenure months, repayments_left = tenure
      - Update customer's current_debt (increase by loan_amount) and persist.
  - If not approved, return loan_id: null and message with reason.
- Response body (201 if created / 400 or 200 with not approved):
  {
    "loan_id": int | null,
    "customer_id": int,
    "loan_approved": boolean,
    "message": "string",
    "monthly_installment": float
  }

4) GET /view-loan/{loan_id}
- Response 200:
  {
    "loan_id": int,
    "customer": {
        "id": int,
        "first_name": string,
        "last_name": string,
        "phone_number": string,
        "age": int
    },
    "loan_amount": float,
    "interest_rate": float,
    "monthly_installment": float,
    "tenure": int
  }
- 404 if loan not found.

5) GET /view-loans/{customer_id}
- Response 200: list of loans (only current/active loans)
Each item:
  {
    "loan_id": int,
    "loan_amount": float,
    "interest_rate": float,
    "monthly_installment": float,
    "repayments_left": int
  }
- 404 if customer not found.

--- Other behavioral details & validations
- Use compound interest (EMI) calculation (already specified above).
- If sum(current loans) > approved_limit => credit_score = 0 and do not approve new loans.
- If sum of active EMIs > 50% of monthly_income => deny.
- Correct interest rate in response if below slab minimum. Example from PDF: "if credit_limit is calculated to be 20 for a particular loan and interest_rate is 8%, send corrected_interest_rate = 16% (lowest of slab)". Implement this as described earlier.
- Round all currency values to 2 decimal places for responses.
- Use proper HTTP status codes:
  - 201 for resource creation
  - 200 for successful checks and fetches
  - 400 for validation errors
  - 404 for not found
  - 500 for server errors

--- Background tasks specifics
- Celery configuration in Django settings. Use Redis as broker and backend in dev.
- Provide a health-check endpoint /health/ (simple 200) used by docker-compose.
- Provide a docker-compose service `ingest` or set the web container entrypoint to run migrations then run `python manage.py ingest_initial_data` which should schedule Celery tasks.
- Include instructions in README to run `docker-compose up --build` and check Celery logs for ingestion summary.

--- Tests & acceptance criteria
Write unit tests for:
- EMI calculation (several test cases incl R=0).
- approved_limit rounding behavior (nearest lakh).
- check-eligibility logic (credit score slabs and corrected_interest_rate).
- create-loan creates Loan and updates Customer.current_debt.

Acceptance (manual tests) that must pass:
1. POST /register should compute approved_limit as 36*salary rounded to nearest 100,000.
2. Provided `/data/customer_data.xlsx` and `/data/loan_data.xlsx` must be ingested by celery tasks scheduled at startup; the tasks should create customers and loans.
3. check-eligibility endpoint must follow the slab rules (approve/deny and correct interest rate when necessary).
4. create-loan must persist loan only when eligible and return null loan_id otherwise.

--- Example curl examples to place into README
1) Register
curl -X POST http://localhost:8000/register -H "Content-Type: application/json" -d '{"first_name":"A","last_name":"B","age":30,"monthly_income":50000,"phone_number":"9999999999"}'

2) Check eligibility
curl -X POST http://localhost:8000/check-eligibility -H "Content-Type: application/json" -d '{"customer_id":1,"loan_amount":200000,"interest_rate":10,"tenure":24}'

3) Create loan
curl -X POST http://localhost:8000/create-loan -H "Content-Type: application/json" -d '{"customer_id":1,"loan_amount":200000,"interest_rate":10,"tenure":24}'

4) View loan
curl http://localhost:8000/view-loan/1

--- Additional deliverables
- README.md with run & test instructions, how ingestion is triggered, and sample responses.
- docker-compose.yml that runs: db (postgres), redis, web (Django + gunicorn), celery_worker, optionally celery_beat.
- Make sure migrations run automatically on container start before scheduling ingestion.
- Provide a small Postman collection or OpenAPI schema auto-generated using drf-spectacular or drf-yasg (optional but nice).

--- Logging & error handling
- Return descriptive error messages on 400 (invalid input), 404 (missing customer/loan).
- Log ingestion errors to file or stdout.
- On Excel ingestion, for rows that fail, include row number and error in the ingestion summary returned to logs.

--- Deliver code quality expectations to Cursor
- Use serializers for validation.
- Views: use APIView or GenericAPIView + mixins (explicit endpoints).
- Keep business logic (credit-score, EMI calc, approved limit rounding) inside a service module (e.g., loans/services.py), unit-test that module.
- Use Decimal for currency math.
- Add type hints where feasible.
- Add at least 5 unit tests covering edge cases.

--- Final note to you (Cursor)
When you generate code, include in repo root a `CHECKLIST.md` showing the assignment spec items and marking them implemented/NA so the reviewer can easily verify requirements in the PDF (I will manually confirm). Also add a `SAMPLE_RESPONSES.md` file showing exact JSON responses for each endpoint (happy paths and key error paths). Remember: all behavior must match the assignment described in the provided PDF exactly. Use the EMI formula and the rating/interest correction rules described above.

Reference: assignment PDF provided. :contentReference[oaicite:1]{index=1}

