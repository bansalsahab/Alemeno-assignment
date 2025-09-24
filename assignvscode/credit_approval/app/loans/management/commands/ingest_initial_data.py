from django.core.management.base import BaseCommand
from loans.tasks import load_customers_from_excel, load_loans_from_excel
import os

class Command(BaseCommand):
    help = 'Schedules Celery tasks to ingest initial customer and loan data from Excel files.'

    def handle(self, *args, **options):
        customer_path = os.getenv('CUSTOMER_DATA_PATH', '/data/customer_data.xlsx')
        loan_path = os.getenv('LOAN_DATA_PATH', '/data/loan_data.xlsx')
        load_customers_from_excel.delay(customer_path)
        load_loans_from_excel.delay(loan_path)
        self.stdout.write(self.style.SUCCESS('Scheduled ingestion tasks for customer and loan data.'))
