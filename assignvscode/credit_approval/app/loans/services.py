from decimal import Decimal, ROUND_HALF_UP
from datetime import date

def round_to_nearest_lakh(value: Decimal) -> Decimal:
    return Decimal(round(value / Decimal('100000'))) * Decimal('100000')

def calculate_emi(principal: Decimal, annual_rate: Decimal, tenure_months: int) -> Decimal:
    if annual_rate == 0:
        emi = principal / Decimal(tenure_months)
    else:
        i = (annual_rate / Decimal('100')) / Decimal('12')
        emi = principal * i * (1 + i) ** tenure_months / ((1 + i) ** tenure_months - 1)
    return emi.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

# Additional business logic for credit score, eligibility, etc. will be implemented here.
