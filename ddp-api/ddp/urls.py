from ddp.views.column_view import ColumnDetailView
from ddp.views.database_view import (
    DatabaseConnectionView,
    DatabaseDetailView,
    DatabaseView,
)
from ddp.views.meta_view import TableMetaExtractView
from ddp.views.table_view import TableDetailView, TableView
from django.urls import path

urlpatterns = [
    # database
    path("db/", view=DatabaseView.as_view(), name="database"),
    path("db/<int:pk>/", view=DatabaseDetailView.as_view(), name="database_detail"),
    path("db/connect/", view=DatabaseConnectionView.as_view(), name="database_connect"),
    # table
    path("db/<int:pk>/table", view=TableView.as_view(), name="table_list"),
    path("table/<int:pk>/", view=TableDetailView.as_view(), name="table_detail"),
    # column
    path("column/<int:pk>/", view=ColumnDetailView.as_view(), name="column_detail"),
    # extract meta
    path("db/<int:pk>/extract/table", view=TableMetaExtractView.as_view(), name="table_extract"),
]
