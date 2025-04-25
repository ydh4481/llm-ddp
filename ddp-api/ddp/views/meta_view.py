from ddp.models import Column, Database, Table
from ddp.serializers import ColumnMetaSerializer
from ddp.services.meta_service import (
    create_tables_and_columns,
    extract_schema_metadata,
    extract_table_metadata,
)
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class SchemaMetaExtractView(APIView):
    """스키마 메타데이터 추출 API"""

    @swagger_auto_schema(
        operation_description="스키마 메타 정보 추출 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "connection_info": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="데이터베이스 접속 정보 (JSON 형식)",
                ),
            },
            required=["connection_info"],
        ),
        responses={
            200: openapi.Response(
                description="스키마 메타데이터 추출 성공",
                examples={
                    "application/json": {
                        "metadata": {
                            "schema1": {"tables": ["table1", "table2"]},
                            "schema2": {"tables": ["table3", "table4"]},
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
    def post(self, request: Request):
        connection_info = request.data.get("connection_info")
        if not connection_info:
            return Response({"message": "Invalid JSON format in connection_info"}, status=404)

        try:
            metadata = extract_schema_metadata(connection_info)
            return Response(metadata, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TableMetaExtractView(APIView):
    """테이블 메타데이터 추출 API"""

    @swagger_auto_schema(
        operation_description="테이블 메타 정보 추출 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "connection_info": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="데이터베이스 접속 정보 (JSON 형식)",
                ),
                "schema_list": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="스키마 리스트",
                ),
            },
            required=["connection_info", "schema_list"],
        ),
        responses={
            200: openapi.Response(
                description="테이블 메타데이터 추출 성공",
                examples={
                    "application/json": {
                        "metadata": [
                            {
                                "schema_name": "schema1",
                                "table_name": "table1",
                                "table_description": "테이블 설명",
                                "columns": ["column1", "column2"],
                            },
                            {
                                "schema_name": "schema2",
                                "table_name": "table2",
                                "table_description": "테이블 설명",
                                "columns": ["column3", "column4"],
                            },
                        ]
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
    def post(self, request: Request):
        connection_info = request.data.get("connection_info")
        if not connection_info:
            return Response({"message": "Invalid JSON format in connection_info"}, status=404)

        schema_list = request.data.get("schema_list", [])
        try:
            metadata = extract_table_metadata(connection_info, schema_list)
            return Response(metadata, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TableMetaView(APIView):
    """테이블 메타 정보 API"""

    def get(self, request: Request, pk: int):
        """메타 정보 상세 조회 API"""
        try:
            tables = Table.objects.filter(database_id=pk)

            meta_info = []
            for table in tables:
                columns = Column.objects.filter(table=table).order_by("column_seq")
                serialized_columns = ColumnMetaSerializer(columns, many=True).data

                meta_info.append(
                    {
                        "schema_name": table.schema_name,
                        "table_name": table.name,
                        "table_description": table.description,
                        "columns": serialized_columns,
                    }
                )

            return Response(meta_info, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request, pk: int):
        """테이블 메타 정보 저장 API"""

        database = Database.objects.get(id=pk)
        if not database:
            return Response({"message": "Database not found"}, status=404)

        metadata = request.data.get("metadata")
        if not metadata:
            return Response({"message": "'metadata' is required"}, status=404)
        try:
            create_tables_and_columns(database, metadata)
            return Response({"message": "Tables and columns created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
