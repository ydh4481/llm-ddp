from langchain_core.messages.ai import AIMessage
from llm.models import LLMLog


def save_llm_log(question: str, ai_response: AIMessage, agent="default") -> None:
    """
    LLM 응답 객체(AIMessage)를 LLMLog 모델로 저장합니다.

    Args:
        question (str): 사용자 질문
        ai_response (AIMessage): LangChain의 LLM 응답 객체
        agent (str): LLM 호출 에이전트 이름
    """
    content = ai_response.content
    metadata = ai_response.response_metadata or {}

    token_usage = metadata.get("token_usage", {})
    prompt_tokens = token_usage.get("prompt_tokens", 0)
    completion_tokens = token_usage.get("completion_tokens", 0)
    total_tokens = token_usage.get("total_tokens", 0)

    log = LLMLog.objects.create(
        id=ai_response.id,
        question=question,
        response_content=content,
        model_name=metadata.get("model_name", ""),
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        agent=agent,
    )

    return log
