from django.contrib import admin
from django import forms
from .models import Auftrag, Container, Box, Item


# Filter widget for existing boxes in container
class ContainerForm(forms.ModelForm):
    boxen = forms.ModelMultipleChoiceField(
        queryset=Box.objects.all(),
        required=False,
        widget=admin.widgets.FilteredSelectMultiple('Boxes', False),
        label='Assign existing boxes',
        help_text='Select already existing boxes'
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
            # Update box assignment
            container.boxen.set(self.cleaned_data['boxen'])
        return container


# Inline for Items in Box
class ItemInline(admin.TabularInline):
    model = Item
    extra = 1
    fields = ('item_id', 'item_name', 'menge')
    readonly_fields = ('item_id',)


# Inline for Boxes in Container (for new creation)
class BoxInline(admin.TabularInline):
    model = Box
    extra = 1
    fields = ('box_id', 'box_name', 'beschreibung')
    readonly_fields = ('box_id',)
    show_change_link = True
    verbose_name = 'Create new box'
    verbose_name_plural = 'Create new boxes'


# Inline for Container in Order
class ContainerInline(admin.TabularInline):
    model = Container
    extra = 1
    fields = ('container_id', 'container_name', 'beschreibung')
    readonly_fields = ('container_id',)
    show_change_link = True


@admin.register(Auftrag)
class AuftragAdmin(admin.ModelAdmin):
    list_display = ('auftrag_id', 'auftragnamen', 'kategorie', 'verfallsdatum', 'status')
    list_filter = ('kategorie', 'verfallsdatum', 'status')
    search_fields = ('auftragnamen', 'kategorie')
    ordering = ('-verfallsdatum',)
    fields = ('auftragnamen', 'kategorie', 'verfallsdatum', 'status')
    readonly_fields = ('status',)
    inlines = [ContainerInline]


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
    get_boxen_count.short_description = 'Number of boxes'


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
    get_auftrag.short_description = 'Order'
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
    get_auftrag.short_description = 'Order'
    get_auftrag.admin_order_field = 'box__container__auftrag'



