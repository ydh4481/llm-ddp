from llm.models import LLMLog
from rest_framework import serializers


class LLMLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = LLMLog
        fields = "__all__"
