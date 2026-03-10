from django.db import models


class Status(models.Model):
    """Status for orders, inspections and positions"""
    status_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    typ = models.CharField(
        max_length=50,
        choices=[
            ('Order', 'Order'),
            ('Inspection', 'Inspection'),
            ('Position', 'Position'),
        ]
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Status"
        verbose_name_plural = "Statuses"
        ordering = ['typ', 'name']
