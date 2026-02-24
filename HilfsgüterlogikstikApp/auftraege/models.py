from django.db import models


class Auftrag(models.Model):
    """Aufträge für Hilfsgüter"""
    
    class AuftragStatus(models.TextChoices):
        OFFEN = 'OFFEN', 'Offen'
        IN_BEARBEITUNG = 'IN_BEARBEITUNG', 'In Bearbeitung'
        IN_PRUEFUNG = 'IN_PRUEFUNG', 'In Prüfung'
        GEPRUEFT = 'GEPRUEFT', 'Geprüft'
        ABGESCHLOSSEN = 'ABGESCHLOSSEN', 'Abgeschlossen'
        STORNIERT = 'STORNIERT', 'Storniert'
    
    auftrag_id = models.AutoField(primary_key=True)
    auftragnamen = models.CharField(max_length=255)
    kategorie = models.CharField(max_length=255)
    verfallsdatum = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=AuftragStatus.choices,
        default=AuftragStatus.OFFEN,
        verbose_name='Status'
    )

    def __str__(self):
        return self.auftragnamen
    
    def aktualisiere_status_von_pruefung(self):
        """Aktualisiert den Status basierend auf der letzten Auftragsprüfung"""
        letzte_pruefung = self.auftragspruefungen.order_by('-datum').first()
        if letzte_pruefung:
            status_mapping = {
                'OFFEN': self.AuftragStatus.IN_PRUEFUNG,
                'IN_PRUEFUNG': self.AuftragStatus.IN_PRUEFUNG,
                'BESTANDEN': self.AuftragStatus.GEPRUEFT,
                'NICHT_BESTANDEN': self.AuftragStatus.IN_BEARBEITUNG,
            }
            self.status = status_mapping.get(
                letzte_pruefung.gesamtstatus,
                self.AuftragStatus.IN_PRUEFUNG
            )
            self.save()

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
