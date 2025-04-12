from django.urls import path
from llm.views.query_execution_view import QueryExecutionView
from llm.views.sql_generation_view import SQLGenerationView

urlpatterns = [
    path("generate-sql/db/<int:database_id>/", SQLGenerationView.as_view(), name="generate-sql"),
    path("execute-sql/db/<int:database_id>/<str:session_id>", QueryExecutionView.as_view(), name="execute-sql"),
]
