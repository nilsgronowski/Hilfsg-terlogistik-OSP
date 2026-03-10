from django.db import models
from django.contrib.auth.models import User


class Rolle(models.Model):
    """Roles for users"""
    rolle_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Role"
        verbose_name_plural = "Roles"
        ordering = ['name']


class Permission(models.Model):
    """Permissions in the system"""
    permission_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['name']


class RolePermission(models.Model):
    """Association of roles and permissions"""
    rolle = models.ForeignKey(Rolle, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.rolle.name} - {self.permission.name}"

    class Meta:
        verbose_name = "RolePermission"
        verbose_name_plural = "RolePermissions"
        unique_together = ('rolle', 'permission')


class UserRolle(models.Model):
    """Association of users and roles"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rolle = models.ForeignKey(Rolle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.rolle.name}"

    class Meta:
        verbose_name = "UserRole"
        verbose_name_plural = "UserRoles"
        unique_together = ('user', 'rolle')
