from rest_framework import serializers

from .models import Column, Database, Table


class DatabaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Database
        fields = "__all__"


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = "__all__"

    def create(self, validated_data):
        """
        database_id, schema_name, name을 고유 키로 확인하여
        중복된 데이터가 있으면 저장하지 않고 기존 객체를 반환합니다.
        """
        database = validated_data.get("database")
        schema_name = validated_data.get("schema_name")
        name = validated_data.get("name")

        # 중복 데이터 확인
        table, created = Table.objects.get_or_create(
            database=database,
            schema_name=schema_name,
            name=name,
            defaults=validated_data,  # 중복이 없을 경우에만 저장
        )

        return table


class ColumnSerializer(serializers.ModelSerializer):
    schema_name = serializers.CharField(source="table.schema_name", read_only=True)

    class Meta:
        model = Column
        fields = "__all__"

    def create(self, validated_data):
        """
        table_id, name을 고유 키로 확인하여
        중복된 데이터가 있으면 저장하지 않고 기존 객체를 반환합니다.
        """
        table = validated_data.get("table")
        name = validated_data.get("name")

        # 중복 데이터 확인
        column, created = Column.objects.get_or_create(
            table=table,
            name=name,
            defaults=validated_data,  # 중복이 없을 경우에만 저장
        )

        return column


class ColumnMetaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = [
            "name",
            "description",
            "data_type",
            "default_value",
            "column_seq",
            "is_nullable",
            "is_primary_key",
            "is_unique",
            "is_foreign_key",
            "foreign_key_table",
            "foreign_key_column",
        ]
