from django.contrib import admin
from auftraege.models import Item
from .models import Pruefung, PruefErgebnis, Schwund


class PruefErgebnisInline(admin.TabularInline):
    model = PruefErgebnis
    extra = 1
    fields = ('pruefergebnis_id', 'item', 'status', 'bemerkung')

    def get_formset(self, request, obj=None, **kwargs):
        request._pruefung_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'item':
            pruefung = getattr(request, '_pruefung_obj', None)
            if pruefung and pruefung.auftrag_id:
                # Hole alle Items aus allen Boxen/Containern dieses Auftrags
                kwargs['queryset'] = Item.objects.filter(
                    box__container__auftrag=pruefung.auftrag
                )
            else:
                kwargs['queryset'] = Item.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


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
