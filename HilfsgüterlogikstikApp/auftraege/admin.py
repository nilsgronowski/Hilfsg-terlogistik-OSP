from django.contrib import admin
from django import forms
from .models import Order, Container, Box, Item


# Filter widget for existing boxes in container
class ContainerForm(forms.ModelForm):
    boxes = forms.ModelMultipleChoiceField(
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
            self.fields['boxes'].initial = self.instance.boxes.all()

    def save(self, commit=True):
        container = super().save(commit=False)
        if commit:
            container.save()
        if container.pk:
            # Update box assignment
            container.boxes.set(self.cleaned_data['boxes'])
        return container


# Inline for Items in Box
class ItemInline(admin.TabularInline):
    model = Item
    extra = 1
    fields = ('item_id', 'name', 'quantity')
    readonly_fields = ('item_id',)


# Inline for Boxes in Container (for new creation)
class BoxInline(admin.TabularInline):
    model = Box
    extra = 1
    fields = ('box_id', 'name', 'description')
    readonly_fields = ('box_id',)
    show_change_link = True
    verbose_name = 'Create new box'
    verbose_name_plural = 'Create new boxes'


# Inline for Container in Order
class ContainerInline(admin.TabularInline):
    model = Container
    extra = 1
    fields = ('container_id', 'name', 'description')
    readonly_fields = ('container_id',)
    show_change_link = True


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'name', 'category', 'expiry_date', 'status')
    list_filter = ('category', 'expiry_date', 'status')
    search_fields = ('name', 'category')
    ordering = ('-expiry_date',)
    fields = ('name', 'category', 'expiry_date', 'status')
    readonly_fields = ('status',)
    inlines = [ContainerInline]


@admin.register(Container)
class ContainerAdmin(admin.ModelAdmin):
    form = ContainerForm
    list_display = ('container_id', 'name', 'order', 'description', 'get_boxes_count')
    list_filter = ('order',)
    search_fields = ('name', 'order__name')
    ordering = ('order', 'container_id')
    fields = ('order', 'name', 'description', 'boxes')
    inlines = [BoxInline]

    def get_boxes_count(self, obj):
        return obj.boxes.count()
    get_boxes_count.short_description = 'Number of boxes'


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ('box_id', 'name', 'container', 'get_order')
    list_filter = ('container__order',)
    search_fields = ('name', 'container__name', 'container__order__name')
    ordering = ('container', 'box_id')
    fields = ('container', 'name', 'description')
    inlines = [ItemInline]

    def get_order(self, obj):
        return obj.container.order.name
    get_order.short_description = 'Order'
    get_order.admin_order_field = 'container__order'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('item_id', 'name', 'quantity', 'box', 'get_container', 'get_order')
    list_filter = ('box__container__order',)
    search_fields = ('name', 'box__name', 'box__container__name')
    ordering = ('box', 'item_id')
    fields = ('box', 'name', 'quantity')

    def get_container(self, obj):
        return obj.box.container.name
    get_container.short_description = 'Container'
    get_container.admin_order_field = 'box__container'

    def get_order(self, obj):
        return obj.box.container.order.name
    get_order.short_description = 'Order'
    get_order.admin_order_field = 'box__container__order'



