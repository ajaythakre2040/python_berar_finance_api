from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_system.utils.pagination import CustomPagination
from dedup.models.apilog import APILog
from dedup.models.loan_account_remark import LoanAccountRemark
from dedup.serializers.loan_account_remark_serializer import LoanAccountRemarkSerializer
from dedup.utils.mis_helpers import call_mis_api
from api_endpoints import CUSTOMER_SEARCH_BY_ADDRESS_URL
from django.db.models import Q
from django.utils.timezone import make_aware


class CustomerByAddressZipcodeView(APIView):
    def post(self, request):
        address = request.data.get("address")
        zipcode = request.data.get("zipcode")
        unique_id = request.data.get("unique_id")

        if not unique_id:
            return Response(
                {
                    "success": False,
                    "status_code": 400,
                    "message": "'unique_id' is required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if APILog.objects.filter(
            uniqid=unique_id,
            endpoint="/customers/search-by-address/",
            response_status=200,
        ).exists():
            return Response(
                {
                    "success": False,
                    "status_code": 402,
                    "message": "Duplicate request: this 'unique_id' has already been used.",
                    "unique_id": unique_id,
                },
                status=402,
            )

        if not address or not zipcode:
            return Response(
                {
                    "success": False,
                    "status_code": 400,
                    "message": "Both 'address' and 'zipcode' are required.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not (isinstance(zipcode, str) and len(zipcode) == 6 and zipcode.isdigit()):
            return Response(
                {
                    "success": False,
                    "status_code": 400,
                    "message": "Invalid zipcode. It must be a 6-digit number.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        params = {"address": address, "zipcode": zipcode}
        mis_response = call_mis_api(
            request, CUSTOMER_SEARCH_BY_ADDRESS_URL, params=params, timeout=30
        )

        if mis_response.status_code != 200:
            return mis_response

        mis_data = mis_response.data.get("data", {})
        return Response(
            {
                "success": True,
                "message": mis_data.get("message", "Data retrieved successfully."),
                "status_code": mis_data.get("status_code", 200),
                "unique_id": unique_id,
                "data": mis_data.get("data", []),
            },
            status=status.HTTP_200_OK,
        )


class LoanAccountRemarkView(APIView):

    def post(self, request):
        serializer = LoanAccountRemarkSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user)
                return Response(
                    {
                        "success": True,
                        "status_code": 201,
                        "message": "Loan account remark added successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "status_code": 402,
                        "message": "Duplicate entry: Failed to add loan account remark.",
                        "errors": str(e),
                    },
                    status=402,
                )

        return Response(
            {
                "success": False,
                "status_code": 400,
                "message": "Validation failed.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def get(self, request):
        search = request.query_params.get("search", "").strip()
        remarks = LoanAccountRemark.objects.all().order_by("-created_at")

        if search:
            remarks = remarks.filter(
                Q(loan_account__icontains=search)
                | Q(loan_id__icontains=search)
                | Q(remark__icontains=search)
            )

        paginator = CustomPagination()
        paginated_remarks = paginator.paginate_queryset(remarks, request)
        serializer = LoanAccountRemarkSerializer(paginated_remarks, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "status_code": 200,
                "message": "Loan account remarks fetched successfully.",
            },
        )
