from django.db import models
from django.contrib.auth.models import User
from auftraege.models import Item, Container


class Auftragspruefung(models.Model):
    """Übergeordnete Prüfung für einen gesamten Auftrag"""
    
    class PruefungStatus(models.TextChoices):
        OFFEN = 'OFFEN', 'Offen'
        IN_PRUEFUNG = 'IN_PRUEFUNG', 'In Prüfung'
        BESTANDEN = 'BESTANDEN', 'Bestanden'
        NICHT_BESTANDEN = 'NICHT_BESTANDEN', 'Nicht bestanden'
        ABGEBROCHEN = 'ABGEBROCHEN', 'Abgebrochen'
    
    auftragspruefung_id = models.AutoField(primary_key=True)
    auftrag = models.ForeignKey('auftraege.Auftrag', on_delete=models.CASCADE, related_name='auftragspruefungen')
    pruefer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    datum = models.DateTimeField(auto_now_add=True)
    gesamtstatus = models.CharField(
        max_length=20,
        choices=PruefungStatus.choices,
        default=PruefungStatus.OFFEN,
        verbose_name='Gesamtstatus'
    )

    def __str__(self):
        return f"Auftragsprüfung {self.auftragspruefung_id} - {self.auftrag.auftragnamen}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Aktualisiere Auftragsstatus nach dem Speichern
        self.auftrag.aktualisiere_status_von_pruefung()

    class Meta:
        verbose_name = "Auftragsprüfung"
        verbose_name_plural = "Auftragsprüfungen"
        ordering = ['-datum']


class Einzelpruefung(models.Model):
    """Einzelne Prüfung innerhalb einer Auftragsprüfung (z.B. für einen Container)"""
    
    class EinzelpruefungStatus(models.TextChoices):
        AUSSTEHEND = 'AUSSTEHEND', 'Ausstehend'
        IN_PRUEFUNG = 'IN_PRUEFUNG', 'In Prüfung'
        VOLLSTAENDIG = 'VOLLSTAENDIG', 'Vollständig'
        MIT_MAENGELN = 'MIT_MAENGELN', 'Mit Mängeln'
        UNVOLLSTAENDIG = 'UNVOLLSTAENDIG', 'Unvollständig'
    
    einzelpruefung_id = models.AutoField(primary_key=True)
    auftragspruefung = models.ForeignKey(Auftragspruefung, on_delete=models.CASCADE, related_name='einzelpruefungen')
    container = models.ForeignKey(Container, on_delete=models.CASCADE, null=True, blank=True, help_text='Container, der geprüft wird')
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
        return f"Einzelprüfung {self.einzelpruefung_id}{container_info}"

    class Meta:
        verbose_name = "Einzelprüfung"
        verbose_name_plural = "Einzelprüfungen"
        ordering = ['auftragspruefung', 'datum']


class PruefErgebnis(models.Model):
    """Inspektionsergebnisse für einzelne Items in einer Einzelprüfung"""
    
    class ErgebnisStatus(models.TextChoices):
        VOLLSTAENDIG = 'VOLLSTAENDIG', 'Vollständig'
        UNVOLLSTAENDIG = 'UNVOLLSTAENDIG', 'Unvollständig'
        BESCHAEDIGT = 'BESCHAEDIGT', 'Beschädigt'
        FEHLT = 'FEHLT', 'Fehlt'
        MANGELHAFT = 'MANGELHAFT', 'Mangelhaft'
    
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
        return f"Prüfergebnis {self.pruefergebnis_id} - {self.item.item_name}"

    class Meta:
        verbose_name = "Prüfergebnis"
        verbose_name_plural = "Prüfergebnisse"
        ordering = ['einzelpruefung', 'pruefergebnis_id']


class Schwund(models.Model):
    """Schwund-Report für eine Auftragsprüfung"""
    
    class SchwundStatus(models.TextChoices):
        GEMELDET = 'GEMELDET', 'Gemeldet'
        IN_BEARBEITUNG = 'IN_BEARBEITUNG', 'In Bearbeitung'
        GEKLAERT = 'GEKLAERT', 'Geklärt'
        ABGESCHLOSSEN = 'ABGESCHLOSSEN', 'Abgeschlossen'
    
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
        return f"Schwund {self.schwund_id} - {self.auftragspruefung.auftrag.auftragnamen}"

    class Meta:
        verbose_name = "Schwund"
        verbose_name_plural = "Schwund"
        ordering = ['-datum']
