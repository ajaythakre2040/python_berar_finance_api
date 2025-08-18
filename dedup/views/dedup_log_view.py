from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from auth_system.utils.pagination import CustomPagination
from dedup.models.apilog import APILog
from dedup.serializers.apilog_serializer import APILogSerializer
from django.db.models import Q
from django.utils.timezone import make_aware
from datetime import datetime, timedelta


class GetAllDedupLogsView(APIView):

    def get(self, request):
        search_query = request.query_params.get("search", "").strip()
        from_date = request.query_params.get("from_date", "").strip()
        to_date = request.query_params.get("to_date", "").strip()

        logs = APILog.objects.filter(method="POST").exclude(
            Q(endpoint__iexact="/api/dedup/master-remarks/") |
            Q(endpoint__iexact="/auth_system/logout/")
        )

        if from_date and to_date:
            try:
                from_dt = make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
                to_dt = make_aware(
                    datetime.strptime(to_date, "%Y-%m-%d")
                    + timedelta(days=1)
                    - timedelta(microseconds=1)
                )
                logs = logs.filter(created_at__range=(from_dt, to_dt))
            except ValueError:
                return Response(
                    {
                        "status": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid date format. Use YYYY-MM-DD for 'from_date' and 'to_date'.",
                        "data": [],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if search_query:
            logs = logs.filter(
                Q(method__icontains=search_query)
                | Q(endpoint__icontains=search_query)
                | Q(uniqid__icontains=search_query)
                | Q(response_status__icontains=search_query)
            )

        logs = logs.order_by("-created_at")

        paginator = CustomPagination()
        page_data = paginator.paginate_queryset(logs, request)
        serializer = APILogSerializer(page_data, many=True)

        message = (
            "Logs fetched successfully."
            if logs.exists()
            else "No logs found for the given filters."
        )
        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": message,
            },
        )


class DedupLogCountView(APIView):

    def get(self, request):
        post_logs_count = (
            APILog.objects.filter(method__iexact="POST")
            .exclude(
                Q(endpoint__iexact="/api/auth_system/login/")
                | Q(endpoint__iexact="/api/dedup/master-remarks/")
            )
            .count()
        )
        return Response(
            {
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": "Total POST log count fetched successfully.",
                "total_count": post_logs_count,
            },
            status=status.HTTP_200_OK,
        )


class AllDedupLogsWithoutPaginationView(APIView):
    def get(self, request):
        from_date = request.query_params.get("from_date", "").strip()
        to_date = request.query_params.get("to_date", "").strip()

        logs = APILog.objects.all().order_by("-created_at")

        if from_date and to_date:
            try:
                from_dt = make_aware(datetime.strptime(from_date, "%Y-%m-%d"))
                to_dt = make_aware(
                    datetime.strptime(to_date, "%Y-%m-%d")
                    + timedelta(days=1)
                    - timedelta(microseconds=1)
                )
                logs = logs.filter(created_at__range=(from_dt, to_dt))
            except ValueError:
                return Response(
                    {
                        "status": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Invalid date format. Use YYYY-MM-DD for 'from_date' and 'to_date'.",
                        "data": [],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = APILogSerializer(logs, many=True)

        return Response(
            {
                "status": True,
                "status_code": status.HTTP_200_OK,
                "message": (
                    "Logs fetched successfully." if logs.exists() else "No logs found."
                ),
                "total_logs": logs.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
