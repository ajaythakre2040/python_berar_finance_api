from rest_framework import serializers
from dedup.models import MasterRemark


class MasterRemarkSerializer(serializers.ModelSerializer):
  

    class Meta:
        model = MasterRemark
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "updated_by",
            "deleted_by",
            "deleted_at",
            "created_at",
            "updated_at",
        ]
