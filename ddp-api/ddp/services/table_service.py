import logging

from ddp.models import Column, Table
from ddp.serializers import ColumnSerializer, TableSerializer
from ddp.utils.mysql_connector import MySQLConnector


def create_tables_and_columns(database, table_list):
    # DB ID 주입
    for table in table_list:
        table["database"] = database.id

    # 테이블 저장
    table_serializer = TableSerializer(data=table_list, many=True)
    table_serializer.is_valid(raise_exception=True)
    table_serializer.save()

    # 컬럼 추출 + 테이블 ID 매핑 + 저장
    connector = MySQLConnector(database)
    columns = connector.get_column_meta(table_serializer.data)
    connector.close()

    column_serializer = ColumnSerializer(data=columns, many=True)
    column_serializer.is_valid(raise_exception=True)
    column_serializer.save()

    return table_serializer.data, column_serializer.data
