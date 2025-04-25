import json
import logging

from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from llm.utils.logger import save_llm_log


def select_relevant_tables(question: str, table_list: list[str], model="gpt-4o-mini", temperature=0) -> list[str]:
    prompt = PromptTemplate(
        input_variables=["question", "table_list"],
        template="""
You are a SQL assistant.

Given the user question and the list of available table names, select only the relevant tables that would be used to answer the question.
Response MUST contain ONLY table ids.
Respond ONLY with the JSON object. No explanation. Do NOT wrap the JSON in triple backticks (NO json).

- Question: {question}
- Available Tables:
{table_list}

Respond in JSON format:
{{ "relevant_tables": [1, 2] }}
""",
    )

    llm = ChatOpenAI(model=model, temperature=temperature)
    chain = prompt | llm
    filled_prompt = prompt.format(question=question, table_list=table_list)
    logging.info(f"[TableSelector] Prompt:\n{filled_prompt}")
    response = chain.invoke({"question": question, "table_list": "\n".join(table_list)})

    save_llm_log(question=question, ai_response=response, agent="table_selector")
    content = response.content
    if "```json" in content:
        content = content.split("```json")[1].strip()
        content = content.split("```")[0].strip()

    response_json = json.loads(content)
    logging.info(f"[TableSelector] Result: {response_json}")

    try:
        return response_json.get("relevant_tables", [])
    except Exception:
        return []
