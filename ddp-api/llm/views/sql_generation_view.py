# llm/views/sql_generation_view.py

import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from llm.agents.query_generator import generate_sql_query
from llm.services.meta_service import get_filtered_metadata_by_llm
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class SQLGenerationView(APIView):
    """자연어 질문 → SQL 쿼리 생성 API"""

    http_method_names = ["post"]

    @swagger_auto_schema(
        operation_description="자연어 질문을 기반으로 SQL 쿼리를 생성합니다.",
        manual_parameters=[
            openapi.Parameter(
                name="database_id",
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                required=True,
                description="타겟 데이터베이스의 ID",
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "question": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="자연어로 된 질문",
                    example="30대 이상 사용자들의 주문 총액을 알려줘",
                )
            },
            required=["question"],
        ),
        responses={
            200: openapi.Response(
                description="SQL 생성 성공",
                examples={
                    "application/json": {
                        "id": "...",
                        "query": "SELECT ... FROM ... WHERE ...;",
                        "result": "SUCCESS",
                    }
                },
            ),
            400: openapi.Response(
                description="잘못된 요청 또는 생성 실패",
                examples={"application/json": {"result": "ERROR"}},
            ),
        },
    )
    def post(self, request: Request, database_id: int):
        question = request.data.get("question", "").strip()
        if not question:
            return Response({"result": "ERROR", "message": "질문이 비어 있습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            meta_info = get_filtered_metadata_by_llm(question=question, database_id=database_id)
            logging.info(f"Meta info: {meta_info}")
            if not meta_info:
                return Response(
                    {"result": "ERROR", "message": "메타 정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
            result_json = generate_sql_query(question=question, meta_info=meta_info)
            return Response(result_json, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"result": "ERROR", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)
