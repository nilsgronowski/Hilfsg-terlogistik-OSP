from django.db import models


class Status(models.Model):
    """Status für Aufträge, Prüfungen und Positionen"""
    status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    typ = models.CharField(
        max_length=50,
        choices=[
            ('Auftrag', 'Auftrag'),
            ('Pruefung', 'Prüfung'),
            ('Position', 'Position'),
        ]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Status"
        ordering = ['typ', 'name']
