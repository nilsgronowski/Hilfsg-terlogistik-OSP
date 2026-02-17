from django.contrib import admin
from .models import Pruefung, PruefErgebnis, Schwund


class PruefErgebnisInline(admin.TabularInline):
    model = PruefErgebnis
    extra = 1
    fields = ('pruefergebnis_id', 'item', 'status', 'bemerkung')


@admin.register(Pruefung)
class PruefungAdmin(admin.ModelAdmin):
    list_display = ('pruefung_id', 'auftrag', 'pruefer', 'datum', 'gesamtstatus')
    list_filter = ('gesamtstatus', 'datum')
    search_fields = ('auftrag__auftragnamen', 'pruefer__username')
    readonly_fields = ('datum',)
    inlines = [PruefErgebnisInline]
    ordering = ('-datum',)


@admin.register(PruefErgebnis)
class PruefErgebnisAdmin(admin.ModelAdmin):
    list_display = ('pruefergebnis_id', 'pruefung', 'item', 'status')
    list_filter = ('status', 'pruefung__auftrag')
    search_fields = ('pruefung__auftrag__auftragnamen', 'bemerkung')
    ordering = ('pruefung', 'pruefergebnis_id')


@admin.register(Schwund)
class SchwundAdmin(admin.ModelAdmin):
    list_display = ('schwund_id', 'auftrag', 'klassifizierung', 'pruefer', 'datum', 'status')
    list_filter = ('status', 'klassifizierung', 'datum')
    search_fields = ('auftrag__auftragnamen', 'klassifizierung', 'notiz')
    readonly_fields = ('datum',)
    ordering = ('-datum',)
