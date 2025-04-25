from collections import defaultdict


def format_metadata_for_prompt(columns: list[dict]) -> str:
    """
    컬럼 메타데이터 리스트를 LLM-friendly 텍스트로 변환합니다.

    Args:
        columns (list): [
            {
                "table": "users",
                "schema_name": "ecommerce",
                "name": "user_id",
                "data_type": "INT",
                "description": "...",
                "is_primary_key": True,
                "is_foreign_key": True,
                "foreign_key_table": "orders",
                "foreign_key_column": "user_id"
            },
            ...
        ]

    Returns:
        str: Prompt에서 사용할 메타 정보 문자열
    """
    table_map = defaultdict(list)
    table_description = defaultdict(str)

    for col in columns:
        table = col.get("table")
        schema = table.schema_name or "default"

        full_table_name = f"{schema}.{table.name}"
        col_name = col["name"]
        dtype = col["data_type"]
        description = col.get("description", "")

        # 기본 라인
        line = f"- {col_name} ({dtype})"
        if description:
            line += f": {description}"

        # 태그 추가
        tags = []
        if col.get("is_primary_key"):
            tags.append("PK")
        if col.get("is_foreign_key"):
            fk_table = col.get("foreign_key_table")
            fk_column = col.get("foreign_key_column")
            if fk_table and fk_column:
                tags.append(f"FK → {fk_table}.{fk_column}")

        if tags:
            line += f" [{' | '.join(tags)}]"

        table_map[full_table_name].append(line)
        table_description[full_table_name] = f"Table: {full_table_name}\nDescription: {table.description}"

    # 최종 출력 구성
    output_lines = []
    for full_table_name, cols in table_map.items():
        output_lines.append(table_description[full_table_name])
        output_lines.extend(cols)
        output_lines.append("")

    return "\n".join(output_lines).strip()
