from django.contrib import admin
from auftraege.models import Item
from .models import Auftragspruefung, Einzelpruefung, PruefErgebnis, Schwund


# Inline für Prüfergebnisse in Einzelprüfung
class PruefErgebnisInline(admin.TabularInline):
    model = PruefErgebnis
    extra = 1
    fields = ('pruefergebnis_id', 'item', 'status', 'bemerkung')
    readonly_fields = ('pruefergebnis_id',)

    def get_formset(self, request, obj=None, **kwargs):
        request._einzelpruefung_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'item':
            einzelpruefung = getattr(request, '_einzelpruefung_obj', None)
            if einzelpruefung and einzelpruefung.container:
                # Hole alle Items aus allen Boxen dieses Containers
                kwargs['queryset'] = Item.objects.filter(box__container=einzelpruefung.container)
            elif einzelpruefung and einzelpruefung.auftragspruefung:
                # Fallback: Alle Items des Auftrags
                kwargs['queryset'] = Item.objects.filter(
                    box__container__auftrag=einzelpruefung.auftragspruefung.auftrag
                )
            else:
                kwargs['queryset'] = Item.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Inline für Einzelprüfungen in Auftragsprüfung
class EinzelpruefungInline(admin.TabularInline):
    model = Einzelpruefung
    extra = 1
    fields = ('einzelpruefung_id', 'container', 'pruefer', 'status', 'bemerkung')
    readonly_fields = ('einzelpruefung_id', 'datum')
    show_change_link = True


# Inline für Schwund in Auftragsprüfung (1:1)
class SchwundInline(admin.StackedInline):
    model = Schwund
    can_delete = False
    fields = ('klassifizierung', 'notiz', 'erstellt_von', 'status')
    readonly_fields = ('datum',)
    verbose_name = 'Schwund-Report'
    verbose_name_plural = 'Schwund-Report'


@admin.register(Auftragspruefung)
class AuftragspruefungAdmin(admin.ModelAdmin):
    list_display = ('auftragspruefung_id', 'auftrag', 'pruefer', 'datum', 'gesamtstatus')
    list_filter = ('gesamtstatus', 'datum')
    search_fields = ('auftrag__auftragnamen', 'pruefer__username')
    readonly_fields = ('datum',)
    fields = ('auftrag', 'pruefer', 'gesamtstatus')
    inlines = [EinzelpruefungInline, SchwundInline]
    ordering = ('-datum',)


@admin.register(Einzelpruefung)
class EinzelpruefungAdmin(admin.ModelAdmin):
    list_display = ('einzelpruefung_id', 'auftragspruefung', 'container', 'pruefer', 'datum', 'status')
    list_filter = ('status', 'datum', 'auftragspruefung__auftrag')
    search_fields = ('auftragspruefung__auftrag__auftragnamen', 'container__container_name', 'bemerkung')
    readonly_fields = ('datum',)
    fields = ('auftragspruefung', 'container', 'pruefer', 'status', 'bemerkung')
    inlines = [PruefErgebnisInline]
    ordering = ('-datum',)


@admin.register(PruefErgebnis)
class PruefErgebnisAdmin(admin.ModelAdmin):
    list_display = ('pruefergebnis_id', 'einzelpruefung', 'item', 'status')
    list_filter = ('status', 'einzelpruefung__auftragspruefung__auftrag')
    search_fields = ('einzelpruefung__auftragspruefung__auftrag__auftragnamen', 'item__item_name', 'bemerkung')
    fields = ('einzelpruefung', 'item', 'status', 'bemerkung')
    ordering = ('einzelpruefung', 'pruefergebnis_id')


@admin.register(Schwund)
class SchwundAdmin(admin.ModelAdmin):
    list_display = ('schwund_id', 'get_auftrag', 'klassifizierung', 'erstellt_von', 'datum', 'status')
    list_filter = ('status', 'klassifizierung', 'datum')
    search_fields = ('auftragspruefung__auftrag__auftragnamen', 'klassifizierung', 'notiz')
    readonly_fields = ('datum',)
    fields = ('auftragspruefung', 'klassifizierung', 'notiz', 'erstellt_von', 'status')
    ordering = ('-datum',)

    def get_auftrag(self, obj):
        return obj.auftragspruefung.auftrag.auftragnamen
    get_auftrag.short_description = 'Auftrag'
    get_auftrag.admin_order_field = 'auftragspruefung__auftrag'
