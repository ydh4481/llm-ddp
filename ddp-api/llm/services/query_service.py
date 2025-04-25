# llm/services/query_executor.py

import json
import logging

from ddp.utils.mysql_connector import MySQLConnector
from llm.agents.result_summarizer import summarize_query_result
from llm.models import LLMLog, QueryExecutionLog


def execute_query(database, summarize: bool = False, session_id=None) -> dict:
    """
    SQL 쿼리를 실행하고, 요약까지 포함한 결과 반환

    Args:
        database: Database 객체
        query (str): 실행할 SQL
        question (str): 질문 (요약할 때 사용)
        summarize (bool): 요약 수행 여부
        llm_log_id (int): LLM 로그 ID (선택 사항)

    Returns:
        dict: {
            "columns": [...],
            "rows": [...],
            "row_count": int,
            "elapsed_ms": float,
            "summary": str,  # summarize=True일 때만
        }
    """
    connector = MySQLConnector(database)
    try:
        import time

        session = LLMLog.objects.get(id=session_id)
        query = json.loads(session.response_content).get("query", "")
        if not query:
            return {"error": "No query provided", "status": "ERROR"}
        question = session.question
        if not question:
            return {"error": "No question provided", "status": "ERROR"}

        logging.info(f"쿼리 실행: {query}")
        start = time.perf_counter()
        connector.cursor.execute(query)
        rows = connector.cursor.fetchall()

        logging.info(f"쿼리 결과: {len(rows)} rows")
        columns = [desc[0] for desc in connector.cursor.description]
        elapsed_ms = round((time.perf_counter() - start) * 1000, 4)

        result = "데이터가 없습니다."
        if summarize and rows:
            result = json.loads(summarize_query_result(question, columns, rows))
            if isinstance(result, dict):
                summary = result.get("summary", "")
                chart = result.get("chart", {})
            else:
                summary = result
                chart = {}

        # 로그 저장
        QueryExecutionLog.objects.create(
            database=database,
            query=query,
            row_count=len(rows),
            elapsed_ms=elapsed_ms,
            llm_log_id=session_id,
        )

        connector.close()
        # 결과 반환
        return {
            "columns": columns,
            "rows": rows,
            "row_count": len(rows),
            "elapsed_ms": elapsed_ms,
            "summary": summary,
            "chart": chart,
        }

    except Exception as e:
        logging.error(f"Error executing query: {str(e)}")
        return {"error": str(e), "status": "ERROR"}
