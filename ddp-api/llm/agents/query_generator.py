# llm_agent/agents/query_generator.py
import json
import logging

from langchain.prompts import PromptTemplate
from langchain_core.messages.ai import AIMessage
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from llm.utils.logger import save_llm_log

# You are an elite data analyst who must generate precise MySQL queries under extreme urgency.
# The fate of the mission depends on generating ONE perfect SQL query that answers the user's question using the metadata provided.
# Your response must be ONLY the final SQL query, formatted correctly, and wrapped in a strict JSON format.
# If the provided metadata is insufficient, return a JSON error format instead.
# Act carefully, think critically, and DO NOT explain anything. Just return the result in JSON.
# This is a mission-critical task. There is no second chance.

# You are an expert MySQL query generator.

# Your task is to create a valid SQL query using the provided metadata and question.
# This is a precision-critical task. You must strictly follow the instructions below:

# ---

# 🔹 Role:
# - You are a highly accurate SQL assistant.
# - You do not make assumptions outside of the given information.

# ---

# 🔹 Input:
# - Meta Info: a list of available tables, columns, types, and their descriptions.
# - Question: a user-provided natural language request.

# ---

# 🔹 Guidelines:
# 1. Use ONLY the information provided in the Meta Info.
# 2. Use all relevant tables and JOIN them properly using foreign keys or matching column names if needed.
# 3. If you can construct a query, output it as a JSON object in the format below.
# 4. If you cannot construct a valid query due to missing information, return an error JSON.
# 5. Do NOT add explanation, comments, or extra text.
# 6. Ensure the SQL syntax is clean and executable in MySQL.

# ---

# 🔹 Response Format:
# If query is possible:
# {
#     "query": "SELECT ... FROM ... WHERE ...;",
#     "result": "SUCCESS"
# }

# If query is NOT possible:
# {
#     "result": "ERROR"
# }

# ---

# Meta Info:
# {meta_info}

# ---


# Question:
# {question}
def build_query_generator_agent(model: str = "gpt-4o", temperature: float = 0) -> Runnable:
    """
    자연어 질문을 SQL 쿼리로 바꾸는 LangChain 에이전트를 생성합니다.

    Args:
        model (str): 사용할 OpenAI 모델
        temperature (float): 창의성 정도 (0은 가장 논리적)

    Returns:
        LLMChain: LangChain 기반 SQL 생성 체인
    """
    prompt = PromptTemplate(
        input_variables=["question", "meta_info"],
        template="""
You are an expert in creating MySQL queries.
You should help me create the MySQL query I need for the 'Question' I give. 
Your answers should ONLY be based on the form given below and should follow the answer and format guidelines.
Use the given 'Meta Info' to create an appropriate query for 'Question'.

- Response Guidelines
1. When the information provided is sufficient, generate a valid query without further explanation of the question.
2. Answer with an error form if the information provided is insufficient.
3. Use all relevant tables from the provided metadata to accurately answer the question.
4. If needed, write a proper JOIN query using foreign key relationships or common columns.
5. Please format the query correctly before answering.
6. Always respond with a valid JSON object in the following format
7. All answers should be in Korean.
8. Date(일자) conditions should be in YYYY-MM-DD format. And timestamp(일시) conditions should be in YYYY-MM-DD HH:MM:SS format.
9. When the user requests time series data by date, it should be converted to a date type, and when requesting data by date, it should be converted to a date type.
10. If there is no specific date or time condition, please use the current date and time based on korea timezone (KST).


- Meta Info
{meta_info}

- Response Format
{{
    "query": "A generated SQL query when context is sufficient.",
    "result": "SUCCESS"
}}

- Error Format
{{
    "result": "ERROR",
    "message": "Explain why the question could not be answered with the current metadata.",
}}

- Question
{question}
""",
    )

    llm = ChatOpenAI(
        model=model,
        temperature=temperature,
    )

    return prompt | llm


def generate_sql_query(question: str, meta_info: str) -> dict:
    """
    자연어 질문과 메타데이터를 기반으로 SQL 쿼리를 생성합니다.

    Args:
        question (str): 사용자의 자연어 질문
        meta_info (str): 테이블/컬럼 설명

    Returns:
        dict: 생성된 SQL 쿼리 JSON 객체
        - 성공: {"query": "SELECT ...", "result": "SUCCESS"}
        - 실패: {"result": "ERROR", "message": "Error message"}
    """
    chain = build_query_generator_agent()
    prompt = chain.first  # PromptTemplate
    filled_prompt = prompt.format(question=question, meta_info=meta_info)
    logging.info(f"[QueryGenerator] Prompt:\n{filled_prompt}")
    response = chain.invoke({"question": question, "meta_info": meta_info})
    try:
        content = response.content

        if "```json" in content:
            content = content.split("```json")[1].strip()
            content = content.split("```")[0].strip()

        logging.info(f"[QueryGenerator] Result: {content}")
        log = save_llm_log(question=question, ai_response=response, agent="query_generator")
        result = json.loads(content)  # Updated to use 'content' instead of 'response.text()'
        result["id"] = log.id
        return result
    except json.JSONDecodeError:
        return {"result": "ERROR", "message": "Invalid response format from LLM"}
