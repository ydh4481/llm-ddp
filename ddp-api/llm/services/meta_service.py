from ddp.models import Column, Database, Table
from django.core.exceptions import ObjectDoesNotExist
from llm.agents.table_selector import select_relevant_tables
from llm.tools.metadata_formatter import format_metadata_for_prompt


def get_formatted_metadata(database_id: int) -> str:
    """
    database_id를 통해 저장된 테이블 + 컬럼 메타 정보에서
    LLM-friendly 메타 정보 문자열을 생성합니다.

    Args:
        database_id (int): Database 모델의 ID

    Returns:
        str: LLM-friendly formatted meta_info string
    """
    try:
        database = Database.objects.get(pk=database_id)
    except ObjectDoesNotExist:
        raise ValueError(f"Database(id={database_id}) not found.")

    # 연결된 테이블 ID 추출
    tables = Table.objects.filter(database=database)
    if not tables.exists():
        raise ValueError("No tables found for the given database.")

    table_ids = list(tables.values_list("id", flat=True))

    # 컬럼 추출
    columns = Column.objects.filter(table_id__in=table_ids).select_related("table")

    # LLM 포맷용 리스트 구성
    column_metadata = []
    for col in columns:
        column_metadata.append(
            {
                "table": col.table,
                "name": col.name,
                "data_type": col.data_type,
                "description": col.description,
                "is_primary_key": col.is_primary_key,
                "is_foreign_key": col.is_foreign_key,
                "foreign_key_table": col.foreign_key_table,
                "foreign_key_column": col.foreign_key_column,
            }
        )

    # 포맷팅
    meta_info = format_metadata_for_prompt(column_metadata)
    return meta_info


def get_table_list(database_id: int) -> list[dict]:
    """
    database_id를 통해 저장된 테이블 리스트를 반환합니다.

    Args:
        database_id (int): Database 모델의 ID

    Returns:
        list[dict]: [
            {
                "id": int,
                "name": str,
                "description": str,
                "created_at": datetime,
                "updated_at": datetime
            },
            ...
        ]
    """
    try:
        database = Database.objects.get(pk=database_id)
    except ObjectDoesNotExist:
        raise ValueError(f"Database(id={database_id}) not found.")

    tables = Table.objects.filter(database=database).values("id", "name", "description")
    return list(tables)


def get_filtered_metadata_by_llm(database_id: int, question: str) -> str:
    """
    질문에 기반하여 LLM이 추출한 테이블만 메타 정보로 포맷합니다.

    Args:
        database_id (int): 대상 Database ID
        question (str): 사용자 질문

    Returns:
        str: LLM-friendly formatted meta_info string
    """
    try:
        database = Database.objects.get(pk=database_id)
    except ObjectDoesNotExist:
        raise ValueError(f"Database(id={database_id}) not found.")

    all_tables = Table.objects.filter(database=database)
    if not all_tables.exists():
        raise ValueError("No tables found for the given database.")

    table_list = []
    for table in all_tables:
        table_list.append(f"[{table.id}] {table.name}: ({table.description})")

    # 질의와 관련된 테이블 추출
    relevant_table_ids = select_relevant_tables(question, table_list)
    if not relevant_table_ids:
        raise ValueError("No relevant tables found by LLM.")

    # 테이블 객체 + 컬럼 추출
    relevant_tables = Table.objects.filter(database=database, id__in=relevant_table_ids)
    columns = Column.objects.filter(table__in=relevant_tables).select_related("table")

    column_metadata = []
    for col in columns:
        column_metadata.append(
            {
                "table": col.table,
                "name": col.name,
                "data_type": col.data_type,
                "description": col.description,
                "is_primary_key": col.is_primary_key,
                "is_foreign_key": col.is_foreign_key,
                "foreign_key_table": col.foreign_key_table,
                "foreign_key_column": col.foreign_key_column,
            }
        )

    return format_metadata_for_prompt(column_metadata)
