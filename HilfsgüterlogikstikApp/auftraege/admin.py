from django.contrib import admin
from .models import Auftrag, Items


class ItemsInline(admin.TabularInline):
    model = Items
    extra = 1
    fields = ('position_id', 'item_name', 'menge')
    fk_name = 'auftrag'


@admin.register(Auftrag)
class AuftragAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'auftragnamen', 'kategorie', 'verfallsdatum')
    list_filter = ('kategorie', 'verfallsdatum')
    search_fields = ('auftragnamen', 'kategorie')
    ordering = ('-verfallsdatum',)
    inlines = [ItemsInline]


@admin.register(Items)
class ItemsAdmin(admin.ModelAdmin):
    list_display = ('position_id', 'auftrag', 'item_name', 'menge')
    list_filter = ('auftrag',)
    search_fields = ('auftrag__auftragnamen', 'item_name')
    ordering = ('auftrag', 'position_id')
