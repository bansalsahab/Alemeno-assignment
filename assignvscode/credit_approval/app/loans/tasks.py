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
                        phone_number=str(row['phone_number']),
                        defaults={
                            'first_name': row['first_name'],
                            'last_name': row['last_name'],
                            'age': row.get('age'),
                            'monthly_income': row['monthly_income'],
                            'approved_limit': round_to_nearest_lakh(Decimal(row['monthly_income']) * 36) if not row.get('approved_limit') else row['approved_limit']
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
                    customer = Customer.objects.get(phone_number=str(row['phone_number']))
                    emi = calculate_emi(Decimal(row['loan_amount']), Decimal(row['annual_interest_rate']), int(row['tenure_months']))
                    loan, created_flag = Loan.objects.update_or_create(
                        customer=customer,
                        loan_amount=row['loan_amount'],
                        tenure_months=row['tenure_months'],
                        defaults={
                            'annual_interest_rate': row['annual_interest_rate'],
                            'monthly_repayment': emi,
                            'emis_paid_on_time': row['emis_paid_on_time'],
                            'start_date': row['start_date'],
                            'end_date': row['end_date'],
                            'is_active': row['is_active'],
                            'repayments_left': row['repayments_left']
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
