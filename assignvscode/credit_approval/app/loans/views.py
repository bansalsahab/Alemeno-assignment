from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Customer, Loan
from .serializers import (
    CustomerSerializer, RegisterCustomerSerializer, LoanSerializer,
    CreateLoanSerializer, CheckEligibilitySerializer
)
from .services import round_to_nearest_lakh, calculate_emi
from django.shortcuts import get_object_or_404
from decimal import Decimal

class RegisterCustomerView(APIView):
    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            approved_limit = round_to_nearest_lakh(Decimal(data['monthly_income']) * 36)
            customer = Customer.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                phone_number=str(data['phone_number']),
                age=data.get('age'),
                monthly_income=data['monthly_income'],
                approved_limit=approved_limit
            )
            resp = {
                "customer_id": customer.customer_id,
                "name": f"{customer.first_name} {customer.last_name}",
                "age": customer.age,
                "monthly_income": float(customer.monthly_income),
                "approved_limit": float(customer.approved_limit),
                "phone_number": customer.phone_number
            }
            return Response(resp, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CheckEligibilityView(APIView):
    def post(self, request):
        # Placeholder: implement full business logic
        return Response({"message": "Not implemented"}, status=501)

class CreateLoanView(APIView):
    def post(self, request):
        # Placeholder: implement full business logic
        return Response({"message": "Not implemented"}, status=501)

class ViewLoanView(APIView):
    def get(self, request, loan_id):
        # Placeholder: implement full business logic
        return Response({"message": "Not implemented"}, status=501)

class ViewLoansView(APIView):
    def get(self, request, customer_id):
        # Placeholder: implement full business logic
        return Response({"message": "Not implemented"}, status=501)

class HealthCheckView(APIView):
    def get(self, request):
        return Response({"status": "ok"}, status=200)
