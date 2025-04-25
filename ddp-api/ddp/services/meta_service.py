from collections import defaultdict

from ddp.models import Database
from ddp.serializers import ColumnSerializer, TableSerializer
from ddp.utils.mysql_connector import MySQLConnector
from django.db import transaction


def extract_schema_metadata(connection_info: str) -> list:
    """
    MySQL 서버로부터 스키마 메타데이터를 추출합니다.

    Args:
        connection_info (str): 접속 정보

    Returns:
        list: 스키마 메타데이터 리스트
    """

    connector = MySQLConnector(connection_info=connection_info)
    metadata = connector.get_schema_meta()
    connector.close()
    return metadata


def extract_table_metadata(connection_info: str, schema_list: list) -> list:
    """
    MySQL 서버로부터 테이블 메타데이터를 추출합니다.

    Args:
        connection_info (str): 접속 정보
        schema_list (list): 스키마 이름 리스트

    Returns:
        list: 테이블 메타데이터 리스트
    """

    connector = MySQLConnector(connection_info=connection_info)
    metadata = connector.get_table_meta(schema_list=schema_list)
    connector.close()

    tables = defaultdict(list)
    for row in metadata:
        table = row["table_name"]
        column = {
            "schema_name": row["schema_name"],
            "table_description": row["table_description"],
            "name": row["name"],
            "description": row["description"],
            "data_type": row["data_type"],
            "default_value": row["default_value"],
            "column_seq": row["column_seq"],
            "is_nullable": row["is_nullable"],
            "is_primary_key": row["is_primary_key"],
            "is_unique": row["is_unique"],
            "is_foreign_key": row["is_foreign_key"],
            "foreign_key_table": row["foreign_key_table"],
            "foreign_key_column": row["foreign_key_column"],
        }  # 컬럼 정보만 추려서 dict 구성

        tables[table].append(column)

    # 변환
    output = []
    for table_name, columns in tables.items():
        tables = []
        output.append(
            {
                "table_name": table_name,
                "table_description": columns[0].get("table_description", ""),  # 중복
                "schema_name": columns[0].get("schema_name", ""),
                "columns": columns,
            }
        )
    return output


def create_tables_and_columns(database: Database, metadata: list) -> tuple:
    """
    데이터베이스에 테이블과 컬럼을 생성합니다.

    Args:
        database (Database): 데이터베이스 객체
        metadata (list): 메타데이터 리스트

    Returns:
        tuple: 생성된 테이블과 컬럼 리스트
    """
    with transaction.atomic():
        # 테이블 생성
        for table in metadata:
            table["database"] = database.id
            table["name"] = table["table_name"]
            table["description"] = table["table_description"]
            columns = table.pop("columns", [])

            table_serializer = TableSerializer(data=table, many=False)
            table_serializer.is_valid(raise_exception=True)
            table_serializer.save()
            table = table_serializer.data

            # 테이블 ID 주입
            for column in columns:
                column["table"] = table["id"]
            # 컬럼 생성
            column_serializer = ColumnSerializer(data=columns, many=True)
            column_serializer.is_valid(raise_exception=True)
            column_serializer.save()
