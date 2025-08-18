from django.db import models


class MasterRemark(models.Model):
    remark_text = models.CharField(max_length=255, unique=True)
    created_by = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_by = models.IntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)
    deleted_by = models.IntegerField(null=True, blank=True, default=0)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "dedup_master_remarks"
        verbose_name = "Master Remark"
        verbose_name_plural = "Master Remarks"

    def __str__(self):
        return self.remark_text
