from rest_framework import serializers
from dedup.models import LoanAccountRemark
from dedup.models.master_remark import MasterRemark
from dedup.models.apilog import APILog
import uuid


class LoanAccountRemarkSerializer(serializers.ModelSerializer):
    remark_text = serializers.SerializerMethodField()

    class Meta:
        model = LoanAccountRemark
        fields = [
            "loan_account",
            "loan_id",
            "remark",
            "remark_text",
            "unique_id",
            "created_by",
            "created_at",
        ]
        read_only_fields = ["created_by", "created_at"]

    def validate_remark(self, value):
        if not MasterRemark.objects.filter(id=value).exists():
            raise serializers.ValidationError(
                "Invalid remark ID: This remark does not exist in master remarks."
            )
        return value

    def get_remark_text(self, obj):
        try:
            master_remark = MasterRemark.objects.get(id=obj.remark)
            return master_remark.remark_text
        except MasterRemark.DoesNotExist:
            return None

    def validate_unique_id(self, value):
        if not value:
            raise serializers.ValidationError("The 'unique_id' field is required.")

        if not APILog.objects.filter(
            uniqid=value, endpoint="/customers/search-by-address/", response_status=200
        ).exists():
            raise serializers.ValidationError(
                "Please provide a valid 'unique_id' that corresponds to a successful address-based customer search request."
            )
        return value

    def validate(self, attrs):
        loan_account = attrs.get("loan_account")
        unique_id = attrs.get("unique_id")

        if LoanAccountRemark.objects.filter(
            loan_account=loan_account, unique_id=unique_id
        ).exists():
            raise serializers.ValidationError(
                "Duplicate 'unique_id': This ID has already been used for the specified loan account."
            )

        return attrs
