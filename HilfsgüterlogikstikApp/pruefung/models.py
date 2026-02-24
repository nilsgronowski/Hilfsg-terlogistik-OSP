from django.db import models
from django.contrib.auth.models import User
from auftraege.models import Item, Container


class Auftragspruefung(models.Model):
    """Overall inspection for a complete order"""
    
    class PruefungStatus(models.TextChoices):
        OFFEN = 'OFFEN', 'Open'
        IN_PRUEFUNG = 'IN_PRUEFUNG', 'In Inspection'
        BESTANDEN = 'BESTANDEN', 'Passed'
        NICHT_BESTANDEN = 'NICHT_BESTANDEN', 'Failed'
        ABGEBROCHEN = 'ABGEBROCHEN', 'Aborted'
    
    auftragspruefung_id = models.AutoField(primary_key=True)
    auftrag = models.ForeignKey('auftraege.Auftrag', on_delete=models.CASCADE, related_name='auftragspruefungen')
    pruefer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    datum = models.DateTimeField(auto_now_add=True)
    gesamtstatus = models.CharField(
        max_length=20,
        choices=PruefungStatus.choices,
        default=PruefungStatus.OFFEN,
        verbose_name='Overall status'
    )

    def __str__(self):
        return f"Order inspection {self.auftragspruefung_id} - {self.auftrag.auftragnamen}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update order status after saving
        self.auftrag.aktualisiere_status_von_pruefung()

    class Meta:
        verbose_name = "Order Inspection"
        verbose_name_plural = "Order Inspections"
        ordering = ['-datum']


class Einzelpruefung(models.Model):
    """Individual inspection within an order inspection (e.g. for a container)"""
    
    class EinzelpruefungStatus(models.TextChoices):
        AUSSTEHEND = 'AUSSTEHEND', 'Pending'
        IN_PRUEFUNG = 'IN_PRUEFUNG', 'In Inspection'
        VOLLSTAENDIG = 'VOLLSTAENDIG', 'Complete'
        MIT_MAENGELN = 'MIT_MAENGELN', 'With Defects'
        UNVOLLSTAENDIG = 'UNVOLLSTAENDIG', 'Incomplete'
    
    einzelpruefung_id = models.AutoField(primary_key=True)
    auftragspruefung = models.ForeignKey(Auftragspruefung, on_delete=models.CASCADE, related_name='einzelpruefungen')
    container = models.ForeignKey(Container, on_delete=models.CASCADE, null=True, blank=True, help_text='Container being inspected')
    pruefer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    datum = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=EinzelpruefungStatus.choices,
        default=EinzelpruefungStatus.AUSSTEHEND,
        verbose_name='Status'
    )
    bemerkung = models.TextField(blank=True)

    def __str__(self):
        container_info = f" - {self.container.container_name}" if self.container else ""
        return f"Individual inspection {self.einzelpruefung_id}{container_info}"

    class Meta:
        verbose_name = "Individual Inspection"
        verbose_name_plural = "Individual Inspections"
        ordering = ['auftragspruefung', 'datum']


class PruefErgebnis(models.Model):
    """Inspection results for individual items in an individual inspection"""
    
    class ErgebnisStatus(models.TextChoices):
        VOLLSTAENDIG = 'VOLLSTAENDIG', 'Complete'
        UNVOLLSTAENDIG = 'UNVOLLSTAENDIG', 'Incomplete'
        BESCHAEDIGT = 'BESCHAEDIGT', 'Damaged'
        FEHLT = 'FEHLT', 'Missing'
        MANGELHAFT = 'MANGELHAFT', 'Defective'
    
    pruefergebnis_id = models.AutoField(primary_key=True)
    einzelpruefung = models.ForeignKey(Einzelpruefung, on_delete=models.CASCADE, related_name='ergebnisse')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=ErgebnisStatus.choices,
        default=ErgebnisStatus.VOLLSTAENDIG,
        verbose_name='Status'
    )
    bemerkung = models.TextField(blank=True)

    def __str__(self):
        return f"Inspection result {self.pruefergebnis_id} - {self.item.item_name}"

    class Meta:
        verbose_name = "Inspection Result"
        verbose_name_plural = "Inspection Results"
        ordering = ['einzelpruefung', 'pruefergebnis_id']


class Schwund(models.Model):
    """Shrinkage report for an order inspection"""
    
    class SchwundStatus(models.TextChoices):
        GEMELDET = 'GEMELDET', 'Reported'
        IN_BEARBEITUNG = 'IN_BEARBEITUNG', 'In Progress'
        GEKLAERT = 'GEKLAERT', 'Resolved'
        ABGESCHLOSSEN = 'ABGESCHLOSSEN', 'Completed'
    
    schwund_id = models.AutoField(primary_key=True)
    auftragspruefung = models.OneToOneField(Auftragspruefung, on_delete=models.CASCADE, related_name='schwund_report')
    klassifizierung = models.CharField(max_length=255)
    notiz = models.TextField()
    erstellt_von = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    datum = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=SchwundStatus.choices,
        default=SchwundStatus.GEMELDET,
        verbose_name='Status'
    )

    def __str__(self):
        return f"Shrinkage {self.schwund_id} - {self.auftragspruefung.auftrag.auftragnamen}"

    class Meta:
        verbose_name = "Shrinkage"
        verbose_name_plural = "Shrinkage"
        ordering = ['-datum']
