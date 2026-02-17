from django.contrib import admin
from .models import Rolle, Permission, RolePermission, UserRolle


@admin.register(Rolle)
class RolleAdmin(admin.ModelAdmin):
    list_display = ('rolle_id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('permission_id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(RolePermission)
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'rolle', 'permission')
    list_filter = ('rolle',)
    search_fields = ('rolle__name', 'permission__name')
    ordering = ('rolle', 'permission')


@admin.register(UserRolle)
class UserRolleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'rolle')
    list_filter = ('rolle',)
    search_fields = ('user__username', 'rolle__name')
    ordering = ('user', 'rolle')
