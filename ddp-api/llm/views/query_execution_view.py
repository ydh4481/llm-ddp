from ddp.models import Database
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from llm.services.query_service import execute_query
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class QueryExecutionView(APIView):
    """
    Query Execution API

    이 API는 주어진 데이터베이스에서 SQL 쿼리를 실행하고 결과를 반환합니다.
    """

    @swagger_auto_schema(
        operation_description="SQL 쿼리 실행 API",
        manual_parameters=[
            openapi.Parameter(
                "summarize",
                openapi.IN_QUERY,
                description="결과 요약 여부 (true/false)",
                type=openapi.TYPE_STRING,
                default="false",
            ),
        ],
        responses={
            200: openapi.Response(
                description="쿼리 실행 성공",
                examples={
                    "application/json": {
                        "data": [
                            {"column1": "value1", "column2": "value2"},
                            {"column1": "value3", "column2": "value4"},
                        ]
                    }
                },
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={"application/json": {"error": "No query provided"}},
            ),
            404: openapi.Response(
                description="데이터베이스를 찾을 수 없음",
                examples={"application/json": {"error": "Database not found"}},
            ),
        },
    )
    def post(self, request, database_id: int, session_id: int):
        """
        SQL 쿼리를 실행하고 결과를 반환합니다.

        Args:
            request (Request): HTTP 요청 객체
            database_id (int): 실행할 데이터베이스의 ID
            session_id (int): LLM 실행 세션 ID

        Returns:
            Response: 실행 결과 또는 오류 메시지
        """
        summarize = request.query_params.get("summarize", "false").lower() == "true"

        try:
            db = Database.objects.get(pk=database_id)
        except Database.DoesNotExist:
            return Response({"error": "Database not found"}, status=status.HTTP_404_NOT_FOUND)

        result = execute_query(database=db, session_id=session_id, summarize=summarize)

        if "error" in result:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(result, status=status.HTTP_200_OK)
