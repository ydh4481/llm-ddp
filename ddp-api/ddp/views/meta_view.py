import json

from ddp.models import Database
from ddp.services.meta_service import extract_table_metadata
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class TableMetaExtractView(APIView):
    """테이블 메타데이터 추출 API"""

    @swagger_auto_schema(
        operation_description="테이블 메타 정보 추출 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "schema_list": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_STRING),
                    description="스키마 이름 목록 (빈 값일 경우 모든 스키마를 조회)",
                ),
            },
            required=[],
        ),
        responses={
            200: openapi.Response(
                description="테이블 메타데이터 추출 성공",
                examples={
                    "application/json": {
                        "metadata": {
                            "test_schema": {
                                "table1": {"columns": ["col1", "col2"]},
                                "table2": {"columns": ["col3", "col4"]},
                            }
                        }
                    }
                },
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={"application/json": {"error": "Invalid JSON format in connection_info"}},
            ),
            404: openapi.Response(
                description="데이터베이스를 찾을 수 없음",
                examples={"application/json": {"error": "Database not found"}},
            ),
            500: openapi.Response(
                description="서버 오류",
                examples={"application/json": {"error": "Internal server error"}},
            ),
        },
    )
    def post(self, request: Request, pk: int):
        try:
            database = Database.objects.get(pk=pk)
        except Database.DoesNotExist:
            return Response({"error": "Database not found"}, status=status.HTTP_404_NOT_FOUND)

        if not database.connection_info:
            return Response({"error": "No connection info provided"}, status=status.HTTP_400_BAD_REQUEST)

        schema_list = request.data.get("schema_list", [])
        try:
            metadata = extract_table_metadata(database, schema_list)
            return Response(metadata, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
