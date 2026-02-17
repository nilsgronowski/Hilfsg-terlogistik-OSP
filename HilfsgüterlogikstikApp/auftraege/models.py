from django.db import models


class Auftrag(models.Model):
    """Aufträge für Hilfsgüter"""
    item_id = models.AutoField(primary_key=True)
    auftragnamen = models.CharField(max_length=255)
    kategorie = models.CharField(max_length=255)
    verfallsdatum = models.DateField()

    def __str__(self):
        return self.auftragnamen

    class Meta:
        verbose_name = "Auftrag"
        verbose_name_plural = "Aufträge"
        ordering = ['-verfallsdatum']


class Items(models.Model):
    """Items/Positionen in Aufträgen"""
    position_id = models.AutoField(primary_key=True)
    auftrag = models.ForeignKey(Auftrag, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    menge = models.IntegerField()

    def __str__(self):
        return f"{self.item_name} (x{self.menge})"

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ['auftrag', 'position_id']
