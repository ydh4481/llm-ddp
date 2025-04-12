from django.db import models


class LLMLog(models.Model):
    id = models.CharField(max_length=128, primary_key=True)  # LLM 호출 ID
    question = models.TextField()
    response_content = models.TextField()
    model_name = models.CharField(max_length=128)
    # 사용량 정보
    prompt_tokens = models.IntegerField()
    completion_tokens = models.IntegerField()
    total_tokens = models.IntegerField()
    agent = models.CharField(max_length=128, blank=True, null=True)  # LLM 호출 에이전트
    # 생성 시간
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "llm_log"


class QueryExecutionLog(models.Model):
    database = models.ForeignKey("ddp.Database", on_delete=models.SET_NULL, null=True)
    query = models.TextField()
    llm_log = models.ForeignKey(LLMLog, on_delete=models.SET_NULL, null=True)
    row_count = models.IntegerField()
    elapsed_ms = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "query_execution_log"
