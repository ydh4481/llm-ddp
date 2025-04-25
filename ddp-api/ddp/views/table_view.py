import logging

from ddp.models import Database, Table
from ddp.serializers import TableSerializer
from ddp.services.table_service import create_tables_and_columns
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class TableView(APIView):
    """테이블 모델 API"""

    http_method_names = ["get", "post"]

    @swagger_auto_schema(
        operation_description="테이블 목록 조회 API",
        responses={
            200: openapi.Response(
                description="테이블 목록 조회 성공",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "name": "테이블1",
                            "schema_name": "schema1",
                            "description": "테이블 설명",
                            "database": 1,
                        },
                        {
                            "id": 2,
                            "name": "테이블2",
                            "schema_name": "schema2",
                            "description": "테이블 설명",
                            "database": 1,
                        },
                    ]
                },
            )
        },
    )
    def get(self, request: Request, pk: int):
        """테이블 목록 조회 API"""
        tables = Table.objects.filter(database_id=pk).all()
        serializer = TableSerializer(tables, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TableDetailView(APIView):
    """테이블 수정 및 삭제 API"""

    http_method_names = ["put", "delete"]

    @swagger_auto_schema(
        operation_description="테이블 수정 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="테이블 한국어 이름",
                ),
                "schema_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="스키마 이름",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="테이블 설명",
                ),
            },
            required=["name", "schema_name"],
        ),
        responses={
            200: openapi.Response(
                description="테이블 수정 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "수정된 테이블",
                        "schema_name": "updated_schema",
                        "description": "수정된 테이블 설명",
                        "database": 1,
                    }
                },
            ),
            404: openapi.Response(
                description="테이블을 찾을 수 없음",
                examples={"application/json": {"error": "Table not found"}},
            ),
        },
    )
    def put(self, request: Request, pk: int):
        """테이블 수정 API"""
        try:
            table = Table.objects.get(pk=pk)
        except Table.DoesNotExist:
            return Response({"message": "Table not found"}, status=404)

        data = request.data
        for field in ["name", "schema_name", "description"]:
            if field in data:
                setattr(table, field, data[field])
        table.save()

        serializer = TableSerializer(table)
        return Response(serializer.data, status=200)

    @swagger_auto_schema(
        operation_description="테이블 삭제 API",
        responses={
            204: openapi.Response(
                description="테이블 삭제 성공",
            ),
            404: openapi.Response(
                description="테이블을 찾을 수 없음",
                examples={"application/json": {"error": "Table not found"}},
            ),
        },
    )
    def delete(self, request: Request, pk: int):
        """테이블 삭제 API"""
        try:
            table = Table.objects.get(pk=pk)
        except Table.DoesNotExist:
            return Response({"message": "Table not found"}, status=404)

        table.delete()
        return Response(status=204)
