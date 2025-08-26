from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.utils import timezone
from django.db import IntegrityError


from auth_system.models.role import Role
from auth_system.permissions.token_valid import IsTokenValid
from auth_system.serializers.role_serializer import RoleSerializer
from auth_system.utils.pagination import CustomPagination
from django.db.models import Q


class RoleListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get(self, request):
        search_query = request.GET.get("search", "").strip()

        roles = Role.objects.filter(deleted_at__isnull=True)

        if search_query:
            roles = roles.filter(
                Q(role_name__icontains=search_query)
                | Q(role_code__icontains=search_query)
            )

        roles = roles.order_by("id")
        paginator = CustomPagination()
        page = paginator.paginate_queryset(roles, request)
        serializer = RoleSerializer(page, many=True)

        return paginator.get_custom_paginated_response(
            data=serializer.data,
            extra_fields={
                "success": True,
                "message": "Roles retrieved successfully.",
            },
        )

    def post(self, request):
        serializer = RoleSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            try:
                role = serializer.save()
                return Response(
                    {
                        "success": True,
                        "message": "Role created successfully.",
                        "data": RoleSerializer(role).data,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError as e:
                return Response(
                    {
                        "success": False,
                        "message": "Database error during role creation.",
                        "errors": str(e),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(
            {
                "success": False,
                "message": "Invalid role data.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class RoleDetailView(APIView):
    permission_classes = [IsAuthenticated, IsTokenValid]

    def get_object(self, pk):
        try:
            return Role.objects.get(pk=pk, deleted_at__isnull=True)
        except Role.DoesNotExist:
            raise NotFound(detail="Role not found.")

    def get(self, request, pk):
        role = self.get_object(pk)
        serializer = RoleSerializer(role)
        return Response(
            {
                "success": True,
                "message": "Role retrieved successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request, pk):
        role = self.get_object(pk)
        serializer = RoleSerializer(
            role, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            role = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Role updated successfully.",
                    "data": RoleSerializer(role).data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "success": False,
                "message": "Failed to update role.",
                "errors": serializer.errors,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, pk):
        role = self.get_object(pk)
        user_id = request.user.id
        now = timezone.now()

        role.deleted_at = now
        role.deleted_by = user_id
        role.save()

        role.permissions.filter(deleted_at__isnull=True).update(
            deleted_at=now, deleted_by=user_id
        )

        return Response(
            {
                "success": True,
                "message": "Role and its permissions deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
