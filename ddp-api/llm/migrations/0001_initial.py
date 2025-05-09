# Generated by Django 5.1.6 on 2025-04-06 20:20

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="LLMLog",
            fields=[
                ("id", models.CharField(max_length=128, primary_key=True, serialize=False)),
                ("question", models.TextField()),
                ("response_content", models.TextField()),
                ("model_name", models.CharField(max_length=128)),
                ("system_fingerprint", models.CharField(blank=True, max_length=128, null=True)),
                ("finish_reason", models.CharField(blank=True, max_length=50, null=True)),
                ("prompt_tokens", models.IntegerField()),
                ("completion_tokens", models.IntegerField()),
                ("total_tokens", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
