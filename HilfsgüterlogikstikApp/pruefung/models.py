from django.db import models
from django.contrib.auth.models import User
from auftraege.models import Item, Container


class OrderInspection(models.Model):
    """Overall inspection for a complete order"""
    
    class InspectionStatus(models.TextChoices):
        OFFEN = 'OFFEN', 'Open'
        IN_PRUEFUNG = 'IN_PRUEFUNG', 'In Inspection'
        BESTANDEN = 'BESTANDEN', 'Passed'
        NICHT_BESTANDEN = 'NICHT_BESTANDEN', 'Failed'
        ABGEBROCHEN = 'ABGEBROCHEN', 'Aborted'
    
    order_inspection_id = models.AutoField(primary_key=True)
    order = models.ForeignKey('auftraege.Order', on_delete=models.CASCADE, related_name='order_inspections', db_column='auftrag_id')
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Inspector', db_column='pruefer_id')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date', db_column='datum')
    overall_status = models.CharField(
        max_length=20,
        choices=InspectionStatus.choices,
        default=InspectionStatus.OFFEN,
        verbose_name='Overall Status',
        db_column='gesamtstatus'
    )

    def __str__(self):
        return f"Order inspection {self.order_inspection_id} - {self.order.name}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update order status after saving
        self.order.update_status_from_inspection()

    class Meta:
        verbose_name = "Order Inspection"
        verbose_name_plural = "Order Inspections"
        ordering = ['-date']


class IndividualInspection(models.Model):
    """Individual inspection within an order inspection (e.g. for a container)"""
    
    class IndividualInspectionStatus(models.TextChoices):
        AUSSTEHEND = 'AUSSTEHEND', 'Pending'
        IN_PRUEFUNG = 'IN_PRUEFUNG', 'In Inspection'
        VOLLSTAENDIG = 'VOLLSTAENDIG', 'Complete'
        MIT_MAENGELN = 'MIT_MAENGELN', 'With Defects'
        UNVOLLSTAENDIG = 'UNVOLLSTAENDIG', 'Incomplete'
    
    individual_inspection_id = models.AutoField(primary_key=True)
    order_inspection = models.ForeignKey(OrderInspection, on_delete=models.CASCADE, related_name='individual_inspections', db_column='auftragspruefung_id')
    container = models.ForeignKey(Container, on_delete=models.CASCADE, null=True, blank=True, help_text='Container being inspected', verbose_name='Container', db_column='container_id')
    inspector = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Inspector', db_column='pruefer_id')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date', db_column='datum')
    status = models.CharField(
        max_length=20,
        choices=IndividualInspectionStatus.choices,
        default=IndividualInspectionStatus.AUSSTEHEND,
        verbose_name='Status',
        db_column='status'
    )
    comment = models.TextField(blank=True, verbose_name='Comment', db_column='bemerkung')

    def __str__(self):
        container_info = f" - {self.container.name}" if self.container else ""
        return f"Individual inspection {self.individual_inspection_id}{container_info}"

    class Meta:
        verbose_name = "Individual Inspection"
        verbose_name_plural = "Individual Inspections"
        ordering = ['order_inspection', 'date']


class InspectionResult(models.Model):
    """Inspection results for individual items in an individual inspection"""
    
    class ResultStatus(models.TextChoices):
        VOLLSTAENDIG = 'VOLLSTAENDIG', 'Complete'
        UNVOLLSTAENDIG = 'UNVOLLSTAENDIG', 'Incomplete'
        BESCHAEDIGT = 'BESCHAEDIGT', 'Damaged'
        FEHLT = 'FEHLT', 'Missing'
        MANGELHAFT = 'MANGELHAFT', 'Defective'
    
    inspection_result_id = models.AutoField(primary_key=True)
    individual_inspection = models.ForeignKey(IndividualInspection, on_delete=models.CASCADE, related_name='results', db_column='einzelpruefung_id')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, verbose_name='Item', db_column='item_id')
    status = models.CharField(
        max_length=20,
        choices=ResultStatus.choices,
        default=ResultStatus.VOLLSTAENDIG,
        verbose_name='Status',
        db_column='status'
    )
    comment = models.TextField(blank=True, verbose_name='Comment', db_column='bemerkung')

    def __str__(self):
        return f"Inspection result {self.inspection_result_id} - {self.item.name}"

    class Meta:
        verbose_name = "Inspection Result"
        verbose_name_plural = "Inspection Results"
        ordering = ['individual_inspection', 'inspection_result_id']


class Shrinkage(models.Model):
    """Shrinkage report for an order inspection"""
    
    class ShrinkageStatus(models.TextChoices):
        GEMELDET = 'GEMELDET', 'Reported'
        IN_BEARBEITUNG = 'IN_BEARBEITUNG', 'In Progress'
        GEKLAERT = 'GEKLAERT', 'Resolved'
        ABGESCHLOSSEN = 'ABGESCHLOSSEN', 'Completed'
    
    shrinkage_id = models.AutoField(primary_key=True)
    order_inspection = models.OneToOneField(OrderInspection, on_delete=models.CASCADE, related_name='shrinkage_report', db_column='auftragspruefung_id')
    classification = models.CharField(max_length=255, verbose_name='Classification', db_column='klassifizierung')
    note = models.TextField(verbose_name='Note', db_column='notiz')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Created By', db_column='erstellt_von_id')
    date = models.DateTimeField(auto_now_add=True, verbose_name='Date', db_column='datum')
    status = models.CharField(
        max_length=20,
        choices=ShrinkageStatus.choices,
        default=ShrinkageStatus.GEMELDET,
        verbose_name='Status',
        db_column='status'
    )

    def __str__(self):
        return f"Shrinkage {self.shrinkage_id} - {self.order_inspection.order.name}"

    class Meta:
        verbose_name = "Shrinkage"
        verbose_name_plural = "Shrinkage"
        ordering = ['-date']
