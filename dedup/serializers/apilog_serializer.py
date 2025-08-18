from rest_framework import serializers
from dedup.models import APILog, MasterRemark


class APILogSerializer(serializers.ModelSerializer):
    request_data = serializers.SerializerMethodField()

    class Meta:
        model = APILog
        fields = [
            "id",
            "uniqid",
            "user",
            "method",
            "endpoint",
            "request_data",
            "response_status",
            "created_at",
        ]

    def get_request_data(self, obj):
        data = obj.request_data

        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    remark_id = item.get("remark")
                    if isinstance(remark_id, int):
                        remark_text = (
                            MasterRemark.objects.filter(id=remark_id)
                            .values_list("remark_text", flat=True)
                            .first()
                        )
                        item["remark"] = (
                            remark_text if remark_text else f"(Invalid ID: {remark_id})"
                        )
        elif isinstance(data, dict):
            remark_id = data.get("remark")
            if isinstance(remark_id, int):
                remark_text = (
                    MasterRemark.objects.filter(id=remark_id)
                    .values_list("remark_text", flat=True)
                    .first()
                )
                data["remark"] = (
                    remark_text if remark_text else f"(Invalid ID: {remark_id})"
                )

        return data
