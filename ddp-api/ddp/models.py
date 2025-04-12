from django.db import models


class Database(models.Model):
    eng_name = models.CharField(max_length=255, db_comment="데이터베이스명")
    kor_name = models.CharField(max_length=255)
    description = models.TextField(db_comment="데이터베이스 설명")
    connection_info = models.TextField(blank=True, null=True, db_comment="데이터베이스 접속 정보 JSON 문자열")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.eng_name


class Table(models.Model):
    database = models.ForeignKey(Database, null=False, blank=False, on_delete=models.CASCADE)
    schema_name = models.CharField(max_length=255, blank=False, null=False)
    eng_name = models.CharField(max_length=255, blank=False, null=False)
    kor_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.eng_name


class Column(models.Model):
    table = models.ForeignKey(Table, on_delete=models.CASCADE)
    eng_name = models.CharField(max_length=255, blank=False, null=False)
    kor_name = models.CharField(max_length=255, blank=False, null=False)
    description = models.TextField(null=True, blank=True)
    data_type = models.TextField()
    column_seq = models.IntegerField(blank=False, null=False, default=-1)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    is_unique = models.BooleanField(default=False)
    is_nullable = models.BooleanField(default=False)
    is_primary_key = models.BooleanField(default=False)
    is_foreign_key = models.BooleanField(default=False)
    foreign_key_table = models.CharField(max_length=255, blank=True, null=True)
    foreign_key_column = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.eng_name
