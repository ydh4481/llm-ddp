from ddp.models import Database
from ddp.serializers import DatabaseSerializer
from ddp.services.database_service import validate_and_check_connection
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class DatabaseView(APIView):
    """데이터베이스 API"""

    http_method_names = ["get", "post"]

    @swagger_auto_schema(
        operation_description="데이터베이스 목록 조회 API",
        responses={
            200: openapi.Response(
                description="데이터베이스 목록 조회 성공",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "name": "테스트DB",
                            "description": "테스트용 데이터베이스",
                            "connection_info": "{...}",
                        }
                    ]
                },
            )
        },
    )
    def get(self, request: Request):
        """데이터베이스 목록 조회 API"""
        databases = Database.objects.all()
        serializer = DatabaseSerializer(databases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="데이터베이스 생성 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="데이터베이스 이름",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="데이터베이스 설명",
                ),
                "connection_info": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="JSON 형식의 데이터베이스 접속 정보 (예: {'host': 'db', 'user': 'root', 'password': 'admin', 'database': 'test'})",
                ),
            },
            required=["name", "connection_info"],
        ),
        responses={
            201: openapi.Response(
                description="데이터베이스 생성 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "테스트DB",
                        "description": "테스트용 데이터베이스",
                        "connection_info": "{...}",
                    }
                },
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={"application/json": {"error": "Invalid data"}},
            ),
        },
    )
    def post(self, request: Request):
        """데이터베이스 생성 API"""
        serializer = DatabaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DatabaseDetailView(APIView):
    """데이터베이스 상세 API"""

    http_method_names = ["get", "put", "delete"]

    @swagger_auto_schema(
        operation_description="데이터베이스 상세 조회 API",
        responses={
            200: openapi.Response(
                description="데이터베이스 상세 조회 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "테스트DB",
                        "description": "테스트용 데이터베이스",
                        "connection_info": "{...}",
                    }
                },
            ),
            404: openapi.Response(
                description="데이터베이스를 찾을 수 없음",
                examples={"application/json": {"error": "Database not found"}},
            ),
        },
    )
    def get(self, request: Request, pk: int):
        """데이터베이스 상세 조회 API"""
        try:
            database = Database.objects.get(pk=pk)
            serializer = DatabaseSerializer(database)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Database.DoesNotExist:
            return Response({"error": "Database not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        operation_description="데이터베이스 수정 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="데이터베이스 이름",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="데이터베이스 설명",
                ),
                "connection_info": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="JSON 형식의 데이터베이스 접속 정보 (예: {'host': 'db', 'user': 'root', 'password': 'admin', 'database': 'test'})",
                ),
            },
            required=[],
        ),
        responses={
            200: openapi.Response(
                description="데이터베이스 수정 성공",
                examples={
                    "application/json": {
                        "id": 1,
                        "name": "업데이트된DB",
                        "description": "수정된 데이터베이스",
                        "connection_info": "{...}",
                    }
                },
            ),
            400: openapi.Response(
                description="잘못된 요청",
                examples={"application/json": {"error": "Invalid data"}},
            ),
            404: openapi.Response(
                description="데이터베이스를 찾을 수 없음",
                examples={"application/json": {"error": "Database not found"}},
            ),
        },
    )
    def put(self, request: Request, pk: int):
        """데이터베이스 수정 API"""
        try:
            database = Database.objects.get(pk=pk)
        except Database.DoesNotExist:
            return Response({"error": "Database not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = DatabaseSerializer(database, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="데이터베이스 삭제 API",
        responses={
            204: openapi.Response(
                description="데이터베이스 삭제 성공",
            ),
            404: openapi.Response(
                description="데이터베이스를 찾을 수 없음",
                examples={"application/json": {"error": "Database not found"}},
            ),
        },
    )
    def delete(self, request: Request, pk: int):
        """데이터베이스 삭제 API"""
        try:
            database = Database.objects.get(pk=pk)
            database.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Database.DoesNotExist:
            return Response({"error": "Database not found"}, status=status.HTTP_404_NOT_FOUND)


class DatabaseConnectionView(APIView):
    """데이터베이스 접속 정보 API"""

    http_method_names = ["post"]

    @swagger_auto_schema(
        operation_description="데이터베이스 접속 정보 조회 API",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "connection_info": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="JSON 형식의 데이터베이스 접속 정보 (예: {'host': 'db', 'user': 'root', 'password': 'admin', 'database': 'test'})",
                ),
            },
            required=["connection_info"],
        ),
        responses={
            200: openapi.Response(
                description="데이터베이스 연결 성공",
                examples={"application/json": {"message": "Connection successful"}},
            ),
            400: openapi.Response(
                description="잘못된 요청 또는 연결 실패",
                examples={"application/json": {"error": "Failed to connect to the database"}},
            ),
        },
    )
    def post(self, request: Request):
        """데이터베이스 접속 정보 조회 API"""
        connection_info_str = request.data.get("connection_info")
        success, message = validate_and_check_connection(connection_info_str)

        if success:
            return Response({"message": message}, status=status.HTTP_200_OK)
        return Response({"error": message}, status=status.HTTP_400_BAD_REQUEST)
