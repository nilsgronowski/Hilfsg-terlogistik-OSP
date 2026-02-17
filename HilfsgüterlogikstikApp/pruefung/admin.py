from django.contrib import admin
from .models import Pruefung, Pruefposition


class PruefpositionInline(admin.TabularInline):
    model = Pruefposition
    extra = 1
    fields = ('pruefposition_id', 'item', 'status', 'bemerkung')


@admin.register(Pruefung)
class PruefungAdmin(admin.ModelAdmin):
    list_display = ('pruefung_id', 'auftrag', 'pruefer', 'datum', 'gesamtstatus')
    list_filter = ('gesamtstatus', 'datum')
    search_fields = ('auftrag__auftragnamen', 'pruefer__username')
    readonly_fields = ('datum',)
    inlines = [PruefpositionInline]
    ordering = ('-datum',)


@admin.register(Pruefposition)
class PruefpositionAdmin(admin.ModelAdmin):
    list_display = ('pruefposition_id', 'pruefung', 'item', 'status')
    list_filter = ('status', 'pruefung__auftrag')
    search_fields = ('pruefung__auftrag__auftragnamen', 'bemerkung')
    ordering = ('pruefung', 'pruefposition_id')
