# Generated by Django 5.1.6 on 2025-04-06 21:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("llm", "0003_queryexecutionlog"),
    ]

    operations = [
        migrations.AddField(
            model_name="llmlog",
            name="agent",
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]
