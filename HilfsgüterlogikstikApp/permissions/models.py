from django.db import models
from django.contrib.auth.models import User


class Rolle(models.Model):
    """Rollen für Benutzer"""
    rolle_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Rolle"
        verbose_name_plural = "Rollen"
        ordering = ['name']


class Permission(models.Model):
    """Berechtigungen im System"""
    permission_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Permission"
        verbose_name_plural = "Permissions"
        ordering = ['name']


class RolePermission(models.Model):
    """Verknüpfung von Rollen und Berechtigungen"""
    rolle = models.ForeignKey(Rolle, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.rolle.name} - {self.permission.name}"

    class Meta:
        verbose_name = "RolePermission"
        verbose_name_plural = "RolePermissions"
        unique_together = ('rolle', 'permission')


class UserRolle(models.Model):
    """Verknüpfung von Benutzern und Rollen"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rolle = models.ForeignKey(Rolle, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.rolle.name}"

    class Meta:
        verbose_name = "UserRolle"
        verbose_name_plural = "UserRollen"
        unique_together = ('user', 'rolle')
