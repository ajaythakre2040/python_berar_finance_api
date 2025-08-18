from rest_framework import serializers
from dedup.models import LoanAccountRemark
from dedup.models.master_remark import MasterRemark


class LoanAccountRemarkSerializer(serializers.ModelSerializer):
    remark_text = serializers.SerializerMethodField()

    class Meta:
        model = LoanAccountRemark
        fields = [
            "loan_account",
            "loan_id",
            "remark",
            "remark_text",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]

    def validate_remark(self, value):
        if not MasterRemark.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Invalid remark ID: does not exist in master remarks."
            )
        return value

    def get_remark_text(self, obj):
        try:
            master_remark = MasterRemark.objects.get(id=obj.remark)
            return master_remark.remark_text
        except MasterRemark.DoesNotExist:
            return None
