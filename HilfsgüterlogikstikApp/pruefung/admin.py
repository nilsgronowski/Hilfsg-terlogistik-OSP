from django.contrib import admin
from auftraege.models import Item
from .models import OrderInspection, IndividualInspection, InspectionResult, Shrinkage


# Inline for inspection results in individual inspection
class InspectionResultInline(admin.TabularInline):
    model = InspectionResult
    extra = 1
    fields = ('inspection_result_id', 'item', 'status', 'comment')
    readonly_fields = ('inspection_result_id',)

    def get_formset(self, request, obj=None, **kwargs):
        request._individual_inspection_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'item':
            individual_inspection = getattr(request, '_individual_inspection_obj', None)
            if individual_inspection and individual_inspection.container:
                # Get all items from all boxes of this container
                kwargs['queryset'] = Item.objects.filter(box__container=individual_inspection.container)
            elif individual_inspection and individual_inspection.order_inspection:
                # Fallback: All items of the order
                kwargs['queryset'] = Item.objects.filter(
                    box__container__order=individual_inspection.order_inspection.order
                )
            else:
                kwargs['queryset'] = Item.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Inline for individual inspections in order inspection
class IndividualInspectionInline(admin.TabularInline):
    model = IndividualInspection
    extra = 1
    fields = ('individual_inspection_id', 'container', 'inspector', 'status', 'comment')
    readonly_fields = ('individual_inspection_id', 'date')
    show_change_link = True

    def get_formset(self, request, obj=None, **kwargs):
        request._order_inspection_obj = obj
        return super().get_formset(request, obj, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'container':
            order_inspection = getattr(request, '_order_inspection_obj', None)
            if order_inspection:
                # Filter containers to only show those from the same order
                from auftraege.models import Container
                kwargs['queryset'] = Container.objects.filter(order=order_inspection.order)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# Inline for shrinkage in order inspection (1:1)
class ShrinkageInline(admin.StackedInline):
    model = Shrinkage
    can_delete = False
    fields = ('classification', 'note', 'created_by', 'status')
    readonly_fields = ('date',)
    verbose_name = 'Shrinkage'
    verbose_name_plural = 'Shrinkage'


@admin.register(OrderInspection)
class OrderInspectionAdmin(admin.ModelAdmin):
    list_display = ('order_inspection_id', 'order', 'inspector', 'date', 'overall_status')
    list_filter = ('overall_status', 'date')
    search_fields = ('order__name', 'inspector__username')
    readonly_fields = ('date',)
    fields = ('order', 'inspector', 'overall_status')
    inlines = [IndividualInspectionInline, ShrinkageInline]
    ordering = ('-date',)


@admin.register(IndividualInspection)
class IndividualInspectionAdmin(admin.ModelAdmin):
    list_display = ('individual_inspection_id', 'order_inspection', 'container', 'inspector', 'date', 'status')
    list_filter = ('status', 'date', 'order_inspection__order')
    search_fields = ('order_inspection__order__name', 'container__name', 'comment')
    readonly_fields = ('date',)
    fields = ('order_inspection', 'container', 'inspector', 'status', 'comment')
    inlines = [InspectionResultInline]
    ordering = ('-date',)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'container':
            # Get the IndividualInspection object if editing
            from auftraege.models import Container
            if request.resolver_match.kwargs.get('object_id'):
                individual_inspection = IndividualInspection.objects.get(pk=request.resolver_match.kwargs['object_id'])
                # Filter containers to only show those from the same order
                kwargs['queryset'] = Container.objects.filter(order=individual_inspection.order_inspection.order)
            elif hasattr(request, '_order_inspection_obj') and request._order_inspection_obj:
                # When creating through inline
                kwargs['queryset'] = Container.objects.filter(order=request._order_inspection_obj.order)
            else:
                # Fallback: show limited selection
                kwargs['queryset'] = Container.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(InspectionResult)
class InspectionResultAdmin(admin.ModelAdmin):
    list_display = ('inspection_result_id', 'individual_inspection', 'item', 'status')
    list_filter = ('status', 'individual_inspection__order_inspection__order')
    search_fields = ('individual_inspection__order_inspection__order__name', 'item__name', 'comment')
    fields = ('individual_inspection', 'item', 'status', 'comment')
    ordering = ('individual_inspection', 'inspection_result_id')


@admin.register(Shrinkage)
class ShrinkageAdmin(admin.ModelAdmin):
    list_display = ('shrinkage_id', 'get_order', 'classification', 'created_by', 'date', 'status')
    list_filter = ('status', 'classification', 'date')
    search_fields = ('order_inspection__order__name', 'classification', 'note')
    readonly_fields = ('date',)
    fields = ('order_inspection', 'classification', 'note', 'created_by', 'status')
    ordering = ('-date',)

    def get_order(self, obj):
        return obj.order_inspection.order.name
    get_order.short_description = 'Order'
    get_order.admin_order_field = 'order_inspection__order'
