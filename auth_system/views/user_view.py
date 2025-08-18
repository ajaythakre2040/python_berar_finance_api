from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.exceptions import NotFound

from auth_system.models.user import TblUser
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.serializers.user import TblUserSerializer


class UserListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsTokenValid]
    queryset = TblUser.objects.filter(deleted_at__isnull=True)
    serializer_class = TblUserSerializer

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "message": "User list fetched successfully.",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UserDetailUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TblUser.objects.filter(deleted_at__isnull=True)
    serializer_class = TblUserSerializer
    lookup_field = "id"

    def get_object(self):
        try:
            return TblUser.objects.get(id=self.kwargs["id"], deleted_at__isnull=True)
        except TblUser.DoesNotExist:
            raise NotFound(detail="User not found.", code=status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "success": True,
                "message": "User details fetched successfully.",
                "status_code": status.HTTP_200_OK,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            instance.updated_by = request.user
            instance.updated_at = timezone.now()
            self.perform_update(serializer)
            return Response(
                {
                    "success": True,
                    "message": "User updated successfully.",
                    "status_code": status.HTTP_200_OK,
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "message": "Validation failed.",
                "status_code": status.HTTP_400_BAD_REQUEST,
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.deleted_by = request.user
        instance.save()
        return Response(
            {
                "success": True,
                "message": "User deleted successfully.",
                "status_code": status.HTTP_200_OK,
            },
            status=status.HTTP_200_OK,
        )
