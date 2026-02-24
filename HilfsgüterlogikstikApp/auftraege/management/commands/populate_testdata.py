from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import connection
from datetime import datetime, timedelta
from auftraege.models import Auftrag, Container, Box, Item
from pruefung.models import Auftragspruefung, Einzelpruefung, PruefErgebnis, Schwund


class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starting test data population...'))

        # Clear existing data
        self.clear_data()

        # Create Groups (Roles)
        self.create_groups()

        # Create Users
        self.create_users()

        # Create Orders
        self.create_auftraege()

        self.stdout.write(self.style.SUCCESS('✅ Test data successfully created!'))

    def clear_data(self):
        """Delete existing test data with FK constraint handling"""
        # Disable foreign key checks for MySQL
        with connection.cursor() as cursor:
            cursor.execute('SET FOREIGN_KEY_CHECKS=0')
        
        try:
            # Delete all test data
            Schwund.objects.all().delete()
            PruefErgebnis.objects.all().delete()
            Einzelpruefung.objects.all().delete()
            Auftragspruefung.objects.all().delete()
            Item.objects.all().delete()
            Box.objects.all().delete()
            Container.objects.all().delete()
            Auftrag.objects.all().delete()
            
            # Delete test users and groups
            User.objects.filter(username__startswith='test_').delete()
            Group.objects.all().delete()
        finally:
            # Re-enable foreign key checks
            with connection.cursor() as cursor:
                cursor.execute('SET FOREIGN_KEY_CHECKS=1')

    def create_groups(self):
        """Create user groups (Roles)"""
        groups = [
            'Administrator',
            'Inspector',
            'Logistician',
            'Viewer',
        ]
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
        self.stdout.write(self.style.SUCCESS('  ✓ Groups created'))

    def create_status(self):
        """Create status entries"""
        statuses = [
            # Order Status
            {'name': 'Open', 'typ': 'Order'},
            {'name': 'In Progress', 'typ': 'Order'},
            {'name': 'Completed', 'typ': 'Order'},
            {'name': 'Cancelled', 'typ': 'Order'},
            # Inspection Status
            {'name': 'Pending', 'typ': 'Inspection'},
            {'name': 'In Inspection', 'typ': 'Inspection'},
            {'name': 'Passed', 'typ': 'Inspection'},
            {'name': 'Failed', 'typ': 'Inspection'},
            # Position Status
            {'name': 'Complete', 'typ': 'Position'},
            {'name': 'Incomplete', 'typ': 'Position'},
            {'name': 'Damaged', 'typ': 'Position'},
        ]
        for status_data in statuses:
            Status.objects.get_or_create(**status_data)
        self.stdout.write(self.style.SUCCESS('  ✓ Statuses created'))

    def create_users(self):
        """Create test users"""
        users_data = [
            {'username': 'test_admin', 'email': 'admin@test.local', 'password': 'testpass123', 'is_staff': True},
            {'username': 'test_inspector', 'email': 'inspector@test.local', 'password': 'testpass123'},
            {'username': 'test_logistician', 'email': 'logistician@test.local', 'password': 'testpass123'},
            {'username': 'test_viewer', 'email': 'viewer@test.local', 'password': 'testpass123'},
        ]

        users = {}
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'is_staff': user_data.get('is_staff', False),
                }
            )
            if created:
                user.set_password(user_data['password'])
                user.save()
            users[user_data['username']] = user

        # Assign users to groups
        admin_group = Group.objects.get(name='Administrator')
        inspector_group = Group.objects.get(name='Inspector')
        logistician_group = Group.objects.get(name='Logistician')
        viewer_group = Group.objects.get(name='Viewer')

        users['test_admin'].groups.add(admin_group)
        users['test_inspector'].groups.add(inspector_group)
        users['test_logistician'].groups.add(logistician_group)
        users['test_viewer'].groups.add(viewer_group)

        self.stdout.write(self.style.SUCCESS('  ✓ Users created'))

    def create_auftraege(self):
        """Create test orders with hierarchical structure"""
        today = datetime.now().date()

        # Create Orders
        auftraege_data = [
            {
                'auftragnamen': 'Emergency Package 1',
                'kategorie': 'Medical Equipment',
                'verfallsdatum': today + timedelta(days=30),
            },
            {
                'auftragnamen': 'Emergency Package 2',
                'kategorie': 'Food',
                'verfallsdatum': today + timedelta(days=60),
            },
            {
                'auftragnamen': 'Winter Supplies',
                'kategorie': 'Blankets & Clothing',
                'verfallsdatum': today + timedelta(days=90),
            },
            {
                'auftragnamen': 'Water & Hygiene',
                'kategorie': 'Consumables',
                'verfallsdatum': today + timedelta(days=45),
            },
        ]

        auftraege = {}
        for auftrag_data in auftraege_data:
            auftrag, _ = Auftrag.objects.get_or_create(**auftrag_data)
            auftraege[auftrag.auftrag_id] = auftrag

        # Create Container for Order 1 (Medical Equipment)
        container1_1 = Container.objects.create(
            auftrag=auftraege[1],
            container_name='Container A1',
            beschreibung='Medical consumables'
        )
        container1_2 = Container.objects.create(
            auftrag=auftraege[1],
            container_name='Container A2',
            beschreibung='Instruments and devices'
        )

        # Create Boxes for Container 1-1
        box1_1_1 = Box.objects.create(
            container=container1_1,
            box_name='Box 1',
            beschreibung='Dressing material'
        )
        box1_1_2 = Box.objects.create(
            container=container1_1,
            box_name='Box 2',
            beschreibung='Disinfectants'
        )

        # Create Items for Boxes in Container 1-1
        Item.objects.create(box=box1_1_1, item_name='Dressing material', menge=100)
        Item.objects.create(box=box1_1_1, item_name='Bandages', menge=500)
        Item.objects.create(box=box1_1_2, item_name='Disinfectant', menge=50)
        Item.objects.create(box=box1_1_2, item_name='Gloves', menge=200)

        # Create Boxes for Container 1-2
        box1_2_1 = Box.objects.create(
            container=container1_2,
            box_name='Box 1',
            beschreibung='Thermometers and stethoscopes'
        )
        Item.objects.create(box=box1_2_1, item_name='Thermometer', menge=30)
        Item.objects.create(box=box1_2_1, item_name='Stethoscope', menge=15)

        # Create Container for Order 2 (Food)
        container2_1 = Container.objects.create(
            auftrag=auftraege[2],
            container_name='Container B1',
            beschreibung='Canned and shelf-stable goods'
        )

        box2_1_1 = Box.objects.create(
            container=container2_1,
            box_name='Box 1',
            beschreibung='Canned food'
        )
        box2_1_2 = Box.objects.create(
            container=container2_1,
            box_name='Box 2',
            beschreibung='Dry goods'
        )

        Item.objects.create(box=box2_1_1, item_name='Canned goods', menge=500)
        Item.objects.create(box=box2_1_1, item_name='Canned vegetables', menge=300)
        Item.objects.create(box=box2_1_2, item_name='Rice', menge=100)
        Item.objects.create(box=box2_1_2, item_name='Pasta', menge=150)

        # Create Container for Order 3 (Winter Supplies)
        container3_1 = Container.objects.create(
            auftrag=auftraege[3],
            container_name='Container C1',
            beschreibung='Textiles'
        )

        box3_1_1 = Box.objects.create(
            container=container3_1,
            box_name='Box 1',
            beschreibung='Blankets'
        )
        box3_1_2 = Box.objects.create(
            container=container3_1,
            box_name='Box 2',
            beschreibung='Winter clothing'
        )

        Item.objects.create(box=box3_1_1, item_name='Wool blankets', menge=200)
        Item.objects.create(box=box3_1_2, item_name='Winter jackets', menge=80)
        Item.objects.create(box=box3_1_2, item_name='Gloves (winter)', menge=120)

        # Create Container for Order 4 (Water & Hygiene)
        container4_1 = Container.objects.create(
            auftrag=auftraege[4],
            container_name='Container D1',
            beschreibung='Water containers'
        )

        box4_1_1 = Box.objects.create(
            container=container4_1,
            box_name='Box 1',
            beschreibung='Drinking water'
        )
        box4_1_2 = Box.objects.create(
            container=container4_1,
            box_name='Box 2',
            beschreibung='Hygiene articles'
        )

        Item.objects.create(box=box4_1_1, item_name='Drinking water', menge=75)
        Item.objects.create(box=box4_1_2, item_name='Soap', menge=200)
        Item.objects.create(box=box4_1_2, item_name='Toothbrushes', menge=150)

        # Create Order Inspections
        inspector = User.objects.get(username='test_inspector')

        for auftrag_id, auftrag in auftraege.items():
            # Create Order Inspection
            auftragspruefung, _ = Auftragspruefung.objects.get_or_create(
                auftrag=auftrag,
                defaults={
                    'pruefer': inspector,
                    'gesamtstatus': Auftragspruefung.PruefungStatus.BESTANDEN,
                }
            )

            # Create Individual Inspections for each Container
            for container in auftrag.container.all():
                einzelpruefung, _ = Einzelpruefung.objects.get_or_create(
                    auftragspruefung=auftragspruefung,
                    container=container,
                    defaults={
                        'pruefer': inspector,
                        'status': Einzelpruefung.EinzelpruefungStatus.VOLLSTAENDIG,
                        'bemerkung': f'Inspection of {container.container_name}',
                    }
                )

                # Create Inspection Results for all Items in all Boxes of this Container
                for box in container.boxen.all():
                    for item in box.items.all():
                        PruefErgebnis.objects.get_or_create(
                            einzelpruefung=einzelpruefung,
                            item=item,
                            defaults={
                                'status': PruefErgebnis.ErgebnisStatus.VOLLSTAENDIG,
                                'bemerkung': 'Quality checked and confirmed',
                            }
                        )

            # Create Shrinkage Report for the first Order Inspection
            if auftrag_id == 1:
                Schwund.objects.get_or_create(
                    auftragspruefung=auftragspruefung,
                    defaults={
                        'klassifizierung': 'Damage',
                        'notiz': 'Packaging damaged during transport',
                        'erstellt_von': inspector,
                        'status': Schwund.SchwundStatus.GEMELDET,
                    }
                )

        self.stdout.write(self.style.SUCCESS('  ✓ Orders, Containers, Boxes, Items and Inspections created'))
