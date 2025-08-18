from django.db import models
from auth_system.models import TblUser
from dedup.models import master_remark


class LoanAccountRemark(models.Model):
    loan_account = models.CharField(max_length=30, db_index=True) 
    loan_id = models.CharField(max_length=30, db_index=True,default=0 )
    remark = models.IntegerField()
    created_by = models.ForeignKey(
        TblUser, on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = "dedup_loan_account_remarks"
        verbose_name = "Loan Account Remark"
        verbose_name_plural = "Loan Account Remarks"

    def __str__(self):
        return f"{self.loan_account} - {self.remark}"
