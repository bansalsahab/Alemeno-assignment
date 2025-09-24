# Sample Responses for credit_approval API

## 1. Register Customer (POST /register)
**201 Created**
```json
{
  "customer_id": 1,
  "name": "A B",
  "age": 30,
  "monthly_income": 50000.0,
  "approved_limit": 1800000.0,
  "phone_number": "9999999999"
}
```

## 2. Check Eligibility (POST /check-eligibility)
**200 OK**
```json
{
  "customer_id": 1,
  "approval": true,
  "interest_rate": 10.0,
  "corrected_interest_rate": 12.0,
  "tenure": 24,
  "monthly_installment": 9407.41,
  "credit_score": 55
}
```

## 3. Create Loan (POST /create-loan)
**201 Created**
```json
{
  "loan_id": 1,
  "customer_id": 1,
  "loan_approved": true,
  "message": "Loan approved and created.",
  "monthly_installment": 9407.41
}
```

**200 Not Approved**
```json
{
  "loan_id": null,
  "customer_id": 1,
  "loan_approved": false,
  "message": "Credit score too low. Loan not approved.",
  "monthly_installment": 0.0
}
```

## 4. View Loan (GET /view-loan/1)
**200 OK**
```json
{
  "loan_id": 1,
  "customer": {
    "id": 1,
    "first_name": "A",
    "last_name": "B",
    "phone_number": "9999999999",
    "age": 30
  },
  "loan_amount": 200000.0,
  "interest_rate": 10.0,
  "monthly_installment": 9407.41,
  "tenure": 24
}
```

## 5. View Loans (GET /view-loans/1)
**200 OK**
```json
[
  {
    "loan_id": 1,
    "loan_amount": 200000.0,
    "interest_rate": 10.0,
    "monthly_installment": 9407.41,
    "repayments_left": 12
  }
]
```

## 6. Health Check (GET /health/)
**200 OK**
```json
{"status": "ok"}
```

## Error Examples
**400 Bad Request**
```json
{"error": "Invalid input."}
```
**404 Not Found**
```json
{"error": "Customer not found."}
```
