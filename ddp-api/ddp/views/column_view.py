from ddp.models import Column
from ddp.serializers import ColumnSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class ColumnDetailView(APIView):
    """
    View to handle updating and deleting a column.
    """

    @swagger_auto_schema(
        operation_description="Column 업데이트 By ID",
        request_body=ColumnSerializer,
        responses={200: ColumnSerializer, 400: "Bad Request", 404: "Not Found"},
    )
    def put(self, request, column_id):
        try:
            column = Column.objects.get(id=column_id)
        except Column.DoesNotExist:
            return Response({"error": "Column not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ColumnSerializer(column, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description="Column 삭제 by ID", responses={204: "No Content", 404: "Not Found"})
    def delete(self, request, column_id):
        try:
            column = Column.objects.get(id=column_id)
        except Column.DoesNotExist:
            return Response({"error": "Column not found"}, status=status.HTTP_404_NOT_FOUND)

        column.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
