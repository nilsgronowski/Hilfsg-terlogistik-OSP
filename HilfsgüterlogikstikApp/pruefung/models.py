from django.db import models
from django.contrib.auth.models import User
from auftraege.models import Items
from core.models import Status


class Pruefung(models.Model):
    """Prüfungen für Aufträge"""
    pruefung_id = models.AutoField(primary_key=True)
    auftrag = models.ForeignKey('auftraege.Auftrag', on_delete=models.CASCADE, related_name='pruefungen')
    pruefer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    datum = models.DateTimeField(auto_now_add=True)
    gesamtstatus = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Prüfung {self.pruefung_id} - {self.auftrag.auftragnamen}"

    class Meta:
        verbose_name = "Prüfung"
        verbose_name_plural = "Prüfungen"
        ordering = ['-datum']


class Pruefposition(models.Model):
    """Positionen in Prüfungen"""
    pruefposition_id = models.AutoField(primary_key=True)
    pruefung = models.ForeignKey(Pruefung, on_delete=models.CASCADE, related_name='positionen')
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    bemerkung = models.TextField(blank=True)

    def __str__(self):
        return f"Prüfposition {self.pruefposition_id}"

    class Meta:
        verbose_name = "Prüfposition"
        verbose_name_plural = "Prüfpositionen"
        ordering = ['pruefung', 'pruefposition_id']
