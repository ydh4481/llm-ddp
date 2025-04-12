from ddp.models import Database
from ddp.utils.mysql_connector import MySQLConnector


def extract_table_metadata(database: Database, schema_list: list) -> list:
    """
    MySQL 서버로부터 테이블 메타데이터를 추출합니다.

    Args:
        database (Database): 대상 DB 객체
        schema_list (list): 스키마 이름 리스트

    Returns:
        list: 테이블 메타데이터 리스트
    """
    connector = MySQLConnector(database)
    metadata = connector.get_table_meta(schema_list=schema_list)
    connector.close()
    return metadata
