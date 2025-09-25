from celery import shared_task
import pandas as pd
from .models import Customer, Loan
from .services import round_to_nearest_lakh, calculate_emi
from django.db import transaction
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

@shared_task
def load_customers_from_excel(path):
    try:
        df = pd.read_excel(path, engine='openpyxl')
        created, updated, errors = 0, 0, []
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    customer, created_flag = Customer.objects.update_or_create(
                        phone_number=str(row['Phone Number']),
                        defaults={
                            'first_name': row['First Name'],
                            'last_name': row['Last Name'],
                            'age': row.get('Age'),
                            'monthly_income': row['Monthly Salary'],
                            'approved_limit': row['Approved Limit'] if not pd.isna(row.get('Approved Limit')) else round_to_nearest_lakh(Decimal(row['Monthly Salary']) * 36)
                        }
                    )
                    if created_flag:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    errors.append({'row': idx+2, 'error': str(e)})
        logger.info(f"Customer ingest: created={created}, updated={updated}, errors={len(errors)}")
        return {'created_count': created, 'updated_count': updated, 'errors': errors}
    except Exception as e:
        logger.error(f"Failed to ingest customers: {e}")
        return {'created_count': 0, 'updated_count': 0, 'errors': [str(e)]}

@shared_task
def load_loans_from_excel(path):
    try:
        df = pd.read_excel(path, engine='openpyxl')
        created, updated, errors = 0, 0, []
        with transaction.atomic():
            for idx, row in df.iterrows():
                try:
                    # Find customer by Customer ID (from Excel)
                    customer = Customer.objects.get(customer_id=int(row['Customer']))
                    emi = calculate_emi(Decimal(row['Loan Amount']), Decimal(row['Interest Rate']), int(row['Tenure']))
                    loan, created_flag = Loan.objects.update_or_create(
                        customer=customer,
                        loan_amount=row['Loan Amount'],
                        tenure_months=row['Tenure'],
                        defaults={
                            'annual_interest_rate': row['Interest Rate'],
                            'monthly_repayment': row['Monthly payment'],
                            'emis_paid_on_time': row['EMIs paid on Time'],
                            'start_date': row['Date of Approval'],
                            'end_date': row['End Date'],
                            'is_active': True,  # Default to True, or adjust as needed
                            'repayments_left': 0  # Set to 0 or calculate if needed
                        }
                    )
                    if created_flag:
                        created += 1
                    else:
                        updated += 1
                except Exception as e:
                    errors.append({'row': idx+2, 'error': str(e)})
        logger.info(f"Loan ingest: created={created}, updated={updated}, errors={len(errors)}")
        return {'created_count': created, 'updated_count': updated, 'errors': errors}
    except Exception as e:
        logger.error(f"Failed to ingest loans: {e}")
        return {'created_count': 0, 'updated_count': 0, 'errors': [str(e)]}
