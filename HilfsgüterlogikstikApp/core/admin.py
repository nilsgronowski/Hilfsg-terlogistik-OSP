from django.contrib import admin
from .models import Status


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('status_id', 'name', 'typ')
    list_filter = ('typ',)
    search_fields = ('name',)
    ordering = ('typ', 'name')
