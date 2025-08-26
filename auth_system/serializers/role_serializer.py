from rest_framework import serializers
from django.utils import timezone
from django.db import transaction

from auth_system.models.role import Role
from auth_system.models.role_permission import RolePermission
from auth_system.serializers.role_permission_serializer import RolePermissionSerializer


class RoleSerializer(serializers.ModelSerializer):
    permission = RolePermissionSerializer(many=True, write_only=True)
    permissions = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Role
        fields = [
            "id",
            "role_name",
            "role_code",
            "permission",
            "permissions",
        ]

    def get_permissions(self, obj):
        active_permissions = obj.permissions.filter(deleted_at__isnull=True)
        return RolePermissionSerializer(active_permissions, many=True).data

    def validate_permission(self, value):
        seen = set()
        for item in value:
            menu_id = item.get("menu_id")
            if menu_id in seen:
                raise serializers.ValidationError(
                    f"Duplicate permission found for menu_id = {menu_id}"
                )
            seen.add(menu_id)
        return value

    def create(self, validated_data):
        permissions_data = validated_data.pop("permission", [])
        request = self.context.get("request")
        user_id = getattr(request.user, "id", None) if request else None

        role = Role.objects.create(
            **validated_data,
            created_by=user_id,
        )

        RolePermission.objects.bulk_create(
            [
                RolePermission(role=role, created_by=user_id, **perm)
                for perm in permissions_data
            ]
        )

        return role

    def update(self, instance, validated_data):
        permissions_data = validated_data.pop("permission", None)
        request = self.context.get("request")
        user_id = getattr(request.user, "id", None) if request else None

        print("🛠 user_id:", user_id)
        print("🛠 validated_data:", validated_data)
        print("🛠 permissions_data:", permissions_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.updated_by = user_id
        instance.updated_at = timezone.now()
        instance.save()

        if permissions_data:
            with transaction.atomic():
                menu_ids = [
                    perm.get("menu_id")
                    for perm in permissions_data
                    if perm.get("menu_id") is not None
                ]

                RolePermission.objects.filter(
                    role=instance, menu_id__in=menu_ids, deleted_at__isnull=True
                ).update(
                    deleted_by=user_id,
                    deleted_at=timezone.now(),
                    updated_by=user_id,
                    updated_at=timezone.now(),
                )

                RolePermission.objects.bulk_create(
                    [
                        RolePermission(role=instance, created_by=user_id, **perm)
                        for perm in permissions_data
                        if perm.get("menu_id") is not None
                    ]
                )

        return instance
