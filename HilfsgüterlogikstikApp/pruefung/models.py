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


class PruefErgebnis(models.Model):
    """Inspektionsergebnisse für einzelne Items in einer Prüfung"""
    pruefergebnis_id = models.AutoField(primary_key=True)
    pruefung = models.ForeignKey(Pruefung, on_delete=models.CASCADE, related_name='ergebnisse')
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    bemerkung = models.TextField(blank=True)

    def __str__(self):
        return f"Prüfergebnis {self.pruefergebnis_id} - {self.item.item_name}"

    class Meta:
        verbose_name = "Prüfergebnis"
        verbose_name_plural = "Prüfergebnisse"
        ordering = ['pruefung', 'pruefergebnis_id']


class Schwund(models.Model):
    """Schwund/Verlust von Hilfsgütern"""
    schwund_id = models.AutoField(primary_key=True)
    auftrag = models.ForeignKey('auftraege.Auftrag', on_delete=models.CASCADE, related_name='schwund')
    klassifizierung = models.CharField(max_length=255)
    notiz = models.TextField()
    pruefer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    datum = models.DateTimeField(auto_now_add=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Schwund {self.schwund_id} - {self.auftrag.auftragnamen}"

    class Meta:
        verbose_name = "Schwund"
        verbose_name_plural = "Schwund"
