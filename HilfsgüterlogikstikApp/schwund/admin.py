from django.contrib import admin
from .models import Schwund


@admin.register(Schwund)
class SchwundAdmin(admin.ModelAdmin):
    list_display = ('schwund_id', 'auftrag', 'klassifizierung', 'pruefer', 'datum', 'status')
    list_filter = ('status', 'klassifizierung', 'datum')
    search_fields = ('auftrag__auftragnamen', 'klassifizierung', 'notiz')
    readonly_fields = ('datum',)
    ordering = ('-datum',)
