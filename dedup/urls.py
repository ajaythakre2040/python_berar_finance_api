from django.urls import path

from dedup.views.dedup_log_view import (
    AllDedupLogsWithoutPaginationView,
    DedupLogCountView,
    GetAllDedupLogsView,
)
from dedup.views.loan_account_remark_view import (
    CustomerByAddressZipcodeView,
    LoanAccountRemarkView,
)
from dedup.views.master_remark_view import (
    MasterRemarkDetailView,
    MasterRemarkListCreateView,
)

urlpatterns = [
    path(
        "customers/search-by-address/",
        CustomerByAddressZipcodeView.as_view(),
        name="customer-search-by-address-proxy",
    ),
    path(
        "loan-account-remarks/",
        LoanAccountRemarkView.as_view(),
        name="loan-account-remarks",
    ),
    path("logs/", GetAllDedupLogsView.as_view(), name="get_all_dedup_logs"),
    path("logs/count/", DedupLogCountView.as_view(), name="dedup-log-count"),
    path(
        "logs/download-all/",
        AllDedupLogsWithoutPaginationView.as_view(),
        name="download-all-dedup-logs",
    ),
    path(
        "master-remarks/",
        MasterRemarkListCreateView.as_view(),
        name="master-remark-list-create",
    ),
    path(
        "master-remarks/<int:pk>/",
        MasterRemarkDetailView.as_view(),
        name="master-remark-detail",
    ),
]
