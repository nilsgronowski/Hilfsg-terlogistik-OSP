from django.db import models
from django.contrib.auth.models import User
from core.models import Status


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
        verbose_name_plural = "Schwunde"
        ordering = ['-datum']
