from django.db import models


class Order(models.Model):
    """Orders for relief supplies"""
    
    class OrderStatus(models.TextChoices):
        OFFEN = 'OFFEN', 'Open'
        IN_BEARBEITUNG = 'IN_BEARBEITUNG', 'In Progress'
        IN_PRUEFUNG = 'IN_PRUEFUNG', 'In Inspection'
        GEPRUEFT = 'GEPRUEFT', 'Inspected'
        ABGESCHLOSSEN = 'ABGESCHLOSSEN', 'Completed'
        STORNIERT = 'STORNIERT', 'Cancelled'
    
    order_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, verbose_name='Name', db_column='auftragnamen')
    category = models.CharField(max_length=255, verbose_name='Category', db_column='kategorie')
    expiry_date = models.DateField(verbose_name='Expiry Date', db_column='verfallsdatum')
    status = models.CharField(
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.OFFEN,
        verbose_name='Status',
        db_column='status'
    )

    def __str__(self):
        return self.name
    
    def update_status_from_inspection(self):
        """Updates the status based on the last order inspection"""
        last_inspection = self.order_inspections.order_by('-date').first()
        if last_inspection:
            status_mapping = {
                'OFFEN': self.OrderStatus.IN_PRUEFUNG,
                'IN_PRUEFUNG': self.OrderStatus.IN_PRUEFUNG,
                'BESTANDEN': self.OrderStatus.GEPRUEFT,
                'NICHT_BESTANDEN': self.OrderStatus.IN_BEARBEITUNG,
            }
            self.status = status_mapping.get(
                last_inspection.overall_status,
                self.OrderStatus.IN_PRUEFUNG
            )
            self.save()

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-expiry_date']


class Container(models.Model):
    """Containers belong to an order"""
    container_id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='containers', db_column='auftrag_id')
    name = models.CharField(max_length=255, verbose_name='Container Name', db_column='container_name')
    description = models.TextField(blank=True, null=True, verbose_name='Description', db_column='beschreibung')

    def __str__(self):
        return f"{self.name} ({self.order.name})"

    class Meta:
        verbose_name = "Container"
        verbose_name_plural = "Containers"
        ordering = ['order', 'container_id']


class Box(models.Model):
    """Boxes belong to a container"""
    box_id = models.AutoField(primary_key=True)
    container = models.ForeignKey(Container, on_delete=models.CASCADE, related_name='boxes', db_column='container_id')
    name = models.CharField(max_length=255, verbose_name='Box Name', db_column='box_name')
    description = models.TextField(blank=True, null=True, verbose_name='Description', db_column='beschreibung')

    def __str__(self):
        return f"{self.name} ({self.container.name})"

    class Meta:
        verbose_name = "Box"
        verbose_name_plural = "Boxes"
        ordering = ['container', 'box_id']


class Item(models.Model):
    """Items/Positions in boxes"""
    item_id = models.AutoField(primary_key=True)
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name='items', db_column='box_id')
    name = models.CharField(max_length=255, verbose_name='Item Name', db_column='item_name')
    quantity = models.IntegerField(verbose_name='Quantity', db_column='menge')

    def __str__(self):
        return f"{self.name} (x{self.quantity})"

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Items"
        ordering = ['box', 'item_id']
