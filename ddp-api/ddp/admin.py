from django.contrib import admin

from .models import Column, Database, Table


class DatabaseAdmin(admin.ModelAdmin):
    pass


class TableAdmin(admin.ModelAdmin):
    pass


class ColumnAdmin(admin.ModelAdmin):
    pass


admin.site.register(Database, DatabaseAdmin)
admin.site.register(Table, TableAdmin)
admin.site.register(Column, ColumnAdmin)
