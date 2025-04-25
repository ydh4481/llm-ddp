import logging

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from llm.utils.logger import save_llm_log


def summarize_query_result(question: str, columns: list[str], rows: list, model="gpt-4o") -> str:
    is_timeseries = any(
        "date" in col.lower() or "at" in col.lower() or "일자" in col or "일시" in col for col in columns
    )
    print(is_timeseries)
    prompt = PromptTemplate(
        input_variables=["question", "columns", "rows", "is_timeseries"],
        template="""
You are a professional data analyst.

Your task is to:
1. Generate a clear and factual Korean summary based on the user's question and the query result.
2. Recommend the most appropriate chart type for visualizing the data.
3. Structure the chart data according to the chart type, so it can be used directly in frontend components.

---

Inputs:
- Question: {question}
- Columns: {columns}
- Rows: {rows}
- Is Time Series: {is_timeseries} (true or false)

---

Instructions:
1. Write a concise summary in **Korean**, based ONLY on the data and question.
2. Avoid assumptions, vague expressions, or embellishments. Be factual and data-driven.
3. Mention important values such as totals, counts, averages, max/min, trends, etc., if relevant.
4. If 'Is Time Series' is true, the summary MUST reflect temporal trends (e.g., increase/decrease over time, peaks, daily/monthly averages) And MUST order the data accordingly.
5. Recommend ONE chart type from the following list:
   - 'line': for time-based trends.
   - 'bar': for categorical comparisons.
   - 'pie': for proportions/distributions.
   - 'scatter': for numeric correlations.
6. Provide 'x_axis' and 'y_axis' labels for 'line', 'bar', and 'scatter' charts.
7. All axis's column_name MUST BE the same as the column names in the query result.
8. Format the 'chart.data' field according to the chart type:

   - For 'bar' and 'line':
     {{
       "type": "bar",
       "x_axis": "<column_name>",
       "y_axis": ["<column_name1>", "<column_name2>", ...]
     }}
   - For 'pie' (no axis labels):
     {{
       "type": "pie"
     }}
   - For 'scatter':
     {{
       "type": "scatter",
       "x_axis": ["<column_name1>", "<column_name2>", ...],
       "y_axis": ["<column_name1>", "<column_name2>", ...],
     }}

---

Respond in the following JSON format:

{{
  "summary": "<Korean summary>",
  "chart": {{
    "type": "<bar | line | pie | scatter>",
    "x_axis": "<label>",    // optional for pie
    "y_axis": "<label>",    // optional for pie
  }}
}}
""",
    )

    llm = ChatOpenAI(model=model, temperature=0)
    chain = prompt | llm
    logging.info(
        f"[ResultSummarizer] Prompt:\n{prompt.format(question=question, columns=columns, rows=rows, is_timeseries=is_timeseries)}"
    )
    result = chain.invoke(
        {"question": question, "columns": ", ".join(columns), "rows": rows, "is_timeseries": is_timeseries}
    )  # 최대 10줄만 사용
    logging.info(f"[ResultSummarizer] Result: {result.content}")
    # LLM 로그 저장 (선택 사항)
    save_llm_log(question=question, ai_response=result, agent="result_summarizer")
    content = result.content
    if "```json" in content:
        content = content.split("```json")[1].strip()
        content = content.split("```")[0].strip()
    return content.strip()
