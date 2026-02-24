from django.contrib import admin
from django import forms
from .models import Auftrag, Container, Box, Item, ItemBestand


# Filter-Widget für bestehende Boxen im Container
class ContainerForm(forms.ModelForm):
    boxen = forms.ModelMultipleChoiceField(
        queryset=Box.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Boxen', False),
        label='Bestehende Boxen zuweisen',
        help_text='Wähle bereits existierende Boxen aus'
    )

    class Meta:
        model = Container
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields['boxen'].initial = self.instance.boxen.all()

    def save(self, commit=True):
        container = super().save(commit=False)
        if commit:
            container.save()
        if container.pk:
            # Aktualisiere die Boxen-Zuordnung
            container.boxen.set(self.cleaned_data['boxen'])
        return container


# Inline für Items in Box
class ItemInline(admin.TabularInline):
    model = Item
    extra = 1
    fields = ('item_id', 'item_name', 'menge')
    readonly_fields = ('item_id',)


# Inline für Boxen in Container (zum Neu-Erstellen)
class BoxInline(admin.TabularInline):
    model = Box
    extra = 1
    fields = ('box_id', 'box_name', 'beschreibung')
    readonly_fields = ('box_id',)
    show_change_link = True
    verbose_name = 'Neue Box erstellen'
    verbose_name_plural = 'Neue Boxen erstellen'


# Inline für Container in Auftrag
class ContainerInline(admin.TabularInline):
    model = Container
    extra = 1
    fields = ('container_id', 'container_name', 'beschreibung')
    readonly_fields = ('container_id',)
    show_change_link = True


# Inline für ungebundene Items in Auftrag
class ItemBestandInline(admin.TabularInline):
    model = ItemBestand
    extra = 1
    fields = ('bestand_id', 'item_name', 'gesamtmenge', 'beschreibung')
    readonly_fields = ('bestand_id',)


@admin.register(Auftrag)
class AuftragAdmin(admin.ModelAdmin):
    list_display = ('auftrag_id', 'auftragnamen', 'kategorie', 'verfallsdatum')
    list_filter = ('kategorie', 'verfallsdatum')
    search_fields = ('auftragnamen', 'kategorie')
    ordering = ('-verfallsdatum',)
    fields = ('auftragnamen', 'kategorie', 'verfallsdatum')
    inlines = [ContainerInline, ItemBestandInline]


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    form = ContainerForm
    list_display = ('container_id', 'container_name', 'auftrag', 'beschreibung', 'get_boxen_count')
    list_filter = ('auftrag',)
    search_fields = ('container_name', 'auftrag__auftragnamen')
    ordering = ('auftrag', 'container_id')
    fields = ('auftrag', 'container_name', 'beschreibung', 'boxen')
    inlines = [BoxInline]

    def get_boxen_count(self, obj):
        return obj.boxen.count()
    get_boxen_count.short_description = 'Anzahl Boxen'


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('box_id', 'box_name', 'container', 'get_auftrag')
    list_filter = ('container__auftrag',)
    search_fields = ('box_name', 'container__container_name', 'container__auftrag__auftragnamen')
    ordering = ('container', 'box_id')
    fields = ('container', 'box_name', 'beschreibung')
    inlines = [ItemInline]

    def get_auftrag(self, obj):
        return obj.container.auftrag.auftragnamen
    get_auftrag.short_description = 'Auftrag'
    get_auftrag.admin_order_field = 'container__auftrag'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'item_name', 'menge', 'box', 'get_container', 'get_auftrag')
    list_filter = ('box__container__auftrag',)
    search_fields = ('item_name', 'box__box_name', 'box__container__container_name')
    ordering = ('box', 'item_id')
    fields = ('box', 'item_name', 'menge')

    def get_container(self, obj):
        return obj.box.container.container_name
    get_container.short_description = 'Container'
    get_container.admin_order_field = 'box__container'

    def get_auftrag(self, obj):
        return obj.box.container.auftrag.auftragnamen
    get_auftrag.short_description = 'Auftrag'
    get_auftrag.admin_order_field = 'box__container__auftrag'


@admin.register(ItemBestand)
class ItemBestandAdmin(admin.ModelAdmin):
    list_display = ('bestand_id', 'item_name', 'gesamtmenge', 'auftrag', 'beschreibung')
    list_filter = ('auftrag',)
    search_fields = ('item_name', 'auftrag__auftragnamen')
    ordering = ('auftrag', 'item_name')
    fields = ('auftrag', 'item_name', 'gesamtmenge', 'beschreibung')
