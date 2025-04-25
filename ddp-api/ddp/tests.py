from ddp.utils.mysql_connector import MySQLConnector
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Column, Database, Table


class DatabaseModelTest(TestCase):
    def setUp(self):
        self.database = Database.objects.create(
            name="테스트DB",
            description="테스트용 데이터베이스",
            connection_info='{"host": "db", "user": "root", "passwd": "admin"}',
        )

    def test_database_creation_api(self):

        client = APIClient()
        data = {
            "name": "API테스트DB",
            "description": "API 테스트용 데이터베이스",
            "connection_info": '{"host": "db", "user": "api_user", "passwd": "api_passwd"}',
        }

        response = client.post("/api/db/", data, format="json")
        self.assertEqual(response.status_code, 201)

        created_database = Database.objects.get(name="API테스트DB")
        self.assertEqual(created_database.name, "API테스트DB")
        self.assertEqual(created_database.description, "API 테스트용 데이터베이스")

    def test_valid_connection(self):
        data = {"connection_info": '{"host": "db", "port": 3306, "database": "test", "user": "test", "passwd": "test"}'}

        response = self.client.post("/api/db/connect/", data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class MySQLConnectorTest(TestCase):
    def setUp(self):
        self.database = Database.objects.create(
            name="ecommerce 테스트 DB",
            description="테스트용 데이터베이스",
            connection_info="{'host': 'test-db', 'db': 'test_ecommerce', 'user': 'root', 'passwd': 'admin'}",
        )
        self.connector = MySQLConnector(self.database)  # Assuming MySQLConnector is the class to test
        self.client = APIClient()

    def tearDown(self):
        # 테스트 데이터베이스 정리
        self.connector.close()

    # def test_get_schema_meta(self):
    #     # MySQLConnector를 사용하여 메타데이터 추출
    #     schema_meta = self.connector.get_schema_meta()
    #     print(f"{schema_meta=}")
    #     self.assertEqual(schema_meta["database"], "test_ecommerce")
    #     self.assertIsInstance(schema_meta["metadata"], list)

    # def test_get_table_meta(self):
    #     # MySQLConnector를 사용하여 테이블 메타데이터 추출

    #     schema_list = self.connector.get_schema_meta()["metadata"]
    #     table_meta = self.connector.get_table_meta(schema_list=schema_list)
    #     print(f"{table_meta=}")
    #     self.assertIsInstance(table_meta["metadata"], list)

    # def test_get_column_meta(self):
    #     # MySQLConnector를 사용하여 컬럼 메타데이터 추출
    #     schema_list = self.connector.get_schema_meta()["metadata"]
    #     table_list = self.connector.get_table_meta(schema_list=schema_list)["metadata"]
    #     print(f"{table_list=}")
    #     column_meta = self.connector.get_column_meta(table_list=table_list)
    #     print(f"{column_meta=}")
    #     # self.assertIsInstance(column_meta["metadata"], list)

    def test_create_table(self):
        # MySQLConnector를 사용하여 테이블 생성
        schema_list = self.connector.get_schema_meta()
        table_list = self.connector.get_table_meta(schema_list=schema_list)
        data = {"table_list": table_list}
        # print(f"{data=}")
        response = self.client.post(f"/api/db/{self.database.id}/table", data, format="json")
        # print(response.json())


# 1. 데이터베이스 연결 테스트
# 2. 스키마 메타데이터 추출
# 3. 선택된 스키마 중에서 테이블 메타데이터 추출
# 4. 선택된 스키마별 선택된 테이블들에서 컬럼 메타데이터 추출
# 5. 테이블 생성 API 테스트
