import json
import logging
from collections import defaultdict
from textwrap import dedent

import MySQLdb
from ddp.models import Database
from MySQLdb.cursors import DictCursor


class MySQLConnector:
    """MySQL 데이터베이스와 연결하고 메타데이터를 추출하는 클래스입니다."""

    def __init__(self, db: Database = None, connection_info=None):
        """
        Args:
            db: 데이터베이스 객체
        """
        self.db = db
        self.connection_info = connection_info or self.db.connection_info
        self.conn = None
        self.cursor = None
        self.connect()

    def close(self):
        """
        커넥션을 닫습니다.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logging.info("MySQL 커넥션 종료")

    def execute(self, sql: str, params=None):
        """
        SQL 쿼리를 실행합니다.

        Args:
            sql (str): 실행할 SQL 쿼리
            params (tuple, optional): 쿼리 파라미터. 기본값은 None.
        """
        try:
            logging.info("쿼리 실행")
            logging.info(dedent(sql))
            self.cursor.execute(sql, params or ())
        except MySQLdb.Error as e:
            logging.error(f"쿼리 실행 실패: {e}")
            raise RuntimeError(f"Failed to execute query: {e}")

    def query(self, sql: str, params=None):
        """
        SQL 쿼리를 실행하고 결과를 반환합니다.

        Args:
            sql (str): 실행할 SQL 쿼리
            params (tuple, optional): 쿼리 파라미터. 기본값은 None.

        Returns:
            list: 쿼리 결과(소문자로 변경)
        """
        self.execute(sql, params)
        data = self.cursor.fetchall()
        if data:
            data = [{k.lower(): v for k, v in row.items()} for row in data]
            logging.info(f"쿼리 결과: {len(data)} rows")
        return data

    @staticmethod
    def check_connection(connection_json: dict) -> bool:
        """
        주어진 접속정보를 사용하여 MySQL에 접속하고, 접속 여부를 반환합니다.

        Args:
            connection_json (dict): MySQL 접속 정보가 담긴 JSON 객체
                - host: MySQL 서버 호스트
                - user: MySQL 사용자명
                - password: MySQL 비밀번호
                - database: 접속할 데이터베이스명
                - port: MySQL 포트 (기본값: 3306)
                - charset: 문자셋 (기본값: utf8mb4)

        Returns:
            bool: 접속 성공 시 True, 실패 시 False
        """
        try:
            logging.info(f"MySQL 접속 시도: {connection_json}")
            connection = MySQLdb.connect(**connection_json)
            connection.close()
            return True
        except MySQLdb.OperationalError as e:
            logging.error(f"Operational Error: {e}")
        except MySQLdb.ProgrammingError as e:
            logging.error(f"Programming Error: {e}")
        except MySQLdb.Error as e:
            logging.error(f"접속 실패: {e}")
        return False

    def connect(self):
        """데이터베이스에 접속해 커넥션을 반환"""

        logging.info(f"DB 접속 시도: {self.connection_info}")

        connection_json = json.loads(self.connection_info)
        try:
            if self.check_connection(connection_json):
                self.conn = MySQLdb.connect(cursorclass=DictCursor, **connection_json)
                self.cursor = self.conn.cursor()  # 커서 초기화
            else:
                raise ConnectionError("Failed to connect to the database.")
        except MySQLdb.Error as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def get_schema_meta(self):
        """
        주어진 데이터베이스의 메타데이터를 추출합니다.

        Returns:
            list: 스키마 메타데이터 리스트
        """
        # 메타데이터 추출 로직을 여기에 추가합니다.
        sql = f"""
            SELECT DISTINCT table_schema as schema_name
            FROM information_schema.tables
            WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys');
        """

        data = self.query(sql)
        logging.info("메타데이터 추출 완료")
        logging.info(f"추출된 메타데이터: {data}")
        return data

    def get_table_meta(self, schema_list: list = None):
        """
        주어진 데이터베이스의 테이블 메타데이터를 추출합니다.

        Args:
            schema_list (list): 스키마 리스트

        Returns:
            list: 테이블 메타데이터 리스트
        """
        where_query = ""
        if schema_list:
            schema_text = ",".join([f"'{schema}'" for schema in schema_list])
            where_query += f" AND c.table_schema IN ({schema_text})"
        # 메타데이터 추출 로직을 여기에 추가합니다.
        sql = f"""
            SELECT 
                c.table_schema AS schema_name,
                c.table_name AS table_name,
                t.table_comment AS table_description,
                c.column_name AS name,
                c.column_comment AS description,
                c.column_type AS data_type,
                c.column_default AS default_value,
                c.ordinal_position AS column_seq,
                CASE c.is_nullable WHEN 'YES' THEN TRUE ELSE FALSE END AS is_nullable,
                CASE c.column_key WHEN 'PRI' THEN TRUE ELSE FALSE END AS is_primary_key,
                CASE c.column_key WHEN 'UNI' THEN TRUE ELSE FALSE END AS is_unique,
                CASE WHEN k.referenced_table_name IS NOT NULL THEN TRUE ELSE FALSE END AS is_foreign_key,
                k.referenced_table_name AS foreign_key_table,
                k.referenced_column_name AS foreign_key_column
            FROM 
                information_schema.columns c
            LEFT JOIN 
                information_schema.key_column_usage k
                ON c.table_schema = k.TABLE_SCHEMA
                AND c.table_name = k.TABLE_NAME
                AND c.column_name = k.COLUMN_NAME
            LEFT JOIN 
                information_schema.tables t
                ON c.table_schema = t.TABLE_SCHEMA
                AND c.table_name = t.TABLE_NAME
            WHERE 1=1
                {where_query}
                AND c.table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
            ORDER BY c.table_schema, c.table_name, c.ordinal_position;
        """

        data = self.query(sql)
        return data
