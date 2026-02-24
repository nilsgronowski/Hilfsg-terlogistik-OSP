from django.db import models


class Auftrag(models.Model):
    """Aufträge für Hilfsgüter"""
    auftrag_id = models.AutoField(primary_key=True)
    auftragnamen = models.CharField(max_length=255)
    kategorie = models.CharField(max_length=255)
    verfallsdatum = models.DateField()

    def __str__(self):
        return self.auftragnamen

    class Meta:
        verbose_name = "Auftrag"
        verbose_name_plural = "Aufträge"
        ordering = ['-verfallsdatum']


class Container(models.Model):
    """Container gehören zu einem Auftrag"""
    container_id = models.AutoField(primary_key=True)
    auftrag = models.ForeignKey(Auftrag, on_delete=models.CASCADE, related_name='container')
    container_name = models.CharField(max_length=255)
    beschreibung = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.container_name} ({self.auftrag.auftragnamen})"

    class Meta:
        verbose_name = "Container"
        verbose_name_plural = "Container"
        ordering = ['auftrag', 'container_id']


class Box(models.Model):
    """Boxen gehören zu einem Container"""
    box_id = models.AutoField(primary_key=True)
    container = models.ForeignKey(Container, on_delete=models.CASCADE, related_name='boxen')
    box_name = models.CharField(max_length=255)
    beschreibung = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.box_name} ({self.container.container_name})"

    class Meta:
        verbose_name = "Box"
        verbose_name_plural = "Boxen"
        ordering = ['container', 'box_id']


class Item(models.Model):
    """Items/Positionen in Boxen"""
    item_id = models.AutoField(primary_key=True)
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='items')
    item_name = models.CharField(max_length=255)
    menge = models.IntegerField()

    def __str__(self):
        return f"{self.item_name} (x{self.menge})"

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ['box', 'item_id']


class ItemBestand(models.Model):
    """Gesamtbestand von Items, die nicht in Boxen gebunden sind"""
    bestand_id = models.AutoField(primary_key=True)
    auftrag = models.ForeignKey(Auftrag, on_delete=models.CASCADE, related_name='item_bestand')
    item_name = models.CharField(max_length=255)
    gesamtmenge = models.IntegerField(default=0)
    beschreibung = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.item_name} - Ungebunden: {self.gesamtmenge}"

    class Meta:
        verbose_name = "Item Bestand (ungebunden)"
        verbose_name_plural = "Item Bestände (ungebunden)"
        ordering = ['auftrag', 'item_name']
