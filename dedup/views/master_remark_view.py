from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db import IntegrityError
from dedup.models import MasterRemark
from dedup.serializers import MasterRemarkSerializer


class MasterRemarkListCreateView(APIView):

    def get(self, request):
        remarks = MasterRemark.objects.filter(deleted_at__isnull=True).order_by("id")
        serializer = MasterRemarkSerializer(remarks, many=True)
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Remarks retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if not request.user or not request.user.id:
            return Response(
                {
                    "success": False,
                    "status_code": status.HTTP_401_UNAUTHORIZED,
                    "message": "User authentication failed. `created_by` is missing.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = MasterRemarkSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save(created_by=request.user.id)
                return Response(
                    {
                        "success": True,
                        "status_code": status.HTTP_201_CREATED,
                        "message": "Remark created successfully.",
                        "data": serializer.data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "status_code": status.HTTP_400_BAD_REQUEST,
                        "message": "Remark creation failed due to a database constraint violation.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Failed to create remark.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class MasterRemarkDetailView(APIView):

    def get_object(self, pk):
        try:
            return MasterRemark.objects.get(pk=pk, deleted_at__isnull=True)
        except MasterRemark.DoesNotExist:
            raise NotFound(detail=f"Remark with id {pk} not found.")

    def get(self, request, pk):
        remark = self.get_object(pk)
        serializer = MasterRemarkSerializer(remark)
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Remark retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        remark = self.get_object(pk)
        data = request.data.copy()
        data["updated_by"] = request.user.id
        data["updated_at"] = timezone.now()
        serializer = MasterRemarkSerializer(remark, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "status_code": status.HTTP_200_OK,
                    "message": "Remark updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "Failed to update remark.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        remark = self.get_object(pk)
        remark.deleted_at = timezone.now()
        remark.deleted_by = request.user.id
        remark.save()
        return Response(
            {
                "success": True,
                "status_code": status.HTTP_200_OK,
                "message": "Remark deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
