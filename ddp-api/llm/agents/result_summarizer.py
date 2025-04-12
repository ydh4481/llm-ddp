import logging

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from llm.utils.logger import save_llm_log


def summarize_query_result(question: str, columns: list[str], rows: list, model="gpt-4o-mini") -> str:
    prompt = PromptTemplate(
        input_variables=["question", "columns", "rows"],
        template="""
You are a professional data analyst.

Given the following question and query result, summarize the result in Korean.

- Question: {question}
- Columns: {columns}
- Rows: {rows}

Provide only the summary text in Korean.
""",
    )

    llm = ChatOpenAI(model=model, temperature=0)
    chain = prompt | llm
    logging.info(f"[ResultSummarizer] Prompt:\n{prompt.format(question=question, columns=columns, rows=rows)}")
    result = chain.invoke({"question": question, "columns": ", ".join(columns), "rows": rows[:10]})  # 최대 10줄만 사용
    logging.info(f"[ResultSummarizer] Result: {result.content}")

    # LLM 로그 저장 (선택 사항)
    save_llm_log(question=question, ai_response=result, agent="result_summarizer")
    return result.content.strip()
