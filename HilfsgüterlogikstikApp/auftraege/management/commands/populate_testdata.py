from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import connection
from datetime import datetime, timedelta
from core.models import Status
from auftraege.models import Auftrag, Container, Box, Item, ItemBestand
from pruefung.models import Pruefung, PruefErgebnis, Schwund


class Command(BaseCommand):
    help = 'Populates the database with test data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 Starte Testdaten-Population...'))

        # Clear existing data
        self.clear_data()

        # Create Groups (Rollen)
        self.create_groups()

        # Create Status
        self.create_status()

        # Create Users
        self.create_users()

        # Create Aufträge
        self.create_auftraege()

        self.stdout.write(self.style.SUCCESS('✅ Testdaten erfolgreich erstellt!'))

    def clear_data(self):
        """Delete existing test data with FK constraint handling"""
        # Disable foreign key checks for MySQL
        with connection.cursor() as cursor:
            cursor.execute('SET FOREIGN_KEY_CHECKS=0')
        
        try:
            # Delete all test data
            Schwund.objects.all().delete()
            PruefErgebnis.objects.all().delete()
            Pruefung.objects.all().delete()
            Item.objects.all().delete()
            ItemBestand.objects.all().delete()
            Box.objects.all().delete()
            Container.objects.all().delete()
            Auftrag.objects.all().delete()
            Status.objects.all().delete()
            
            # Delete test users and groups
            User.objects.filter(username__startswith='test_').delete()
            Group.objects.all().delete()
        finally:
            # Re-enable foreign key checks
            with connection.cursor() as cursor:
                cursor.execute('SET FOREIGN_KEY_CHECKS=1')

    def create_groups(self):
        """Create user groups (Rollen)"""
        groups = [
            'Administrator',
            'Prüfer',
            'Logistiker',
            'Viewer',
        ]
        for group_name in groups:
            Group.objects.get_or_create(name=group_name)
        self.stdout.write(self.style.SUCCESS('  ✓ Gruppen erstellt'))

    def create_status(self):
        """Create status entries"""
        statuses = [
            # Auftrag Status
            {'name': 'Offen', 'typ': 'Auftrag'},
            {'name': 'In Bearbeitung', 'typ': 'Auftrag'},
            {'name': 'Abgeschlossen', 'typ': 'Auftrag'},
            {'name': 'Storniert', 'typ': 'Auftrag'},
            # Prüfung Status
            {'name': 'Ausstehend', 'typ': 'Pruefung'},
            {'name': 'In Prüfung', 'typ': 'Pruefung'},
            {'name': 'Bestanden', 'typ': 'Pruefung'},
            {'name': 'Nicht bestanden', 'typ': 'Pruefung'},
            # Position Status
            {'name': 'Vollständig', 'typ': 'Position'},
            {'name': 'Unvollständig', 'typ': 'Position'},
            {'name': 'Beschädigt', 'typ': 'Position'},
        ]
        for status_data in statuses:
            Status.objects.get_or_create(**status_data)
        self.stdout.write(self.style.SUCCESS('  ✓ Status erstellt'))

    def create_users(self):
        """Create test users"""
        users_data = [
            {'username': 'test_admin', 'email': 'admin@test.local', 'password': 'testpass123', 'is_staff': True},
            {'username': 'test_pruefer', 'email': 'pruefer@test.local', 'password': 'testpass123'},
            {'username': 'test_logistiker', 'email': 'logistiker@test.local', 'password': 'testpass123'},
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
        pruefer_group = Group.objects.get(name='Prüfer')
        logistiker_group = Group.objects.get(name='Logistiker')
        viewer_group = Group.objects.get(name='Viewer')

        users['test_admin'].groups.add(admin_group)
        users['test_pruefer'].groups.add(pruefer_group)
        users['test_logistiker'].groups.add(logistiker_group)
        users['test_viewer'].groups.add(viewer_group)

        self.stdout.write(self.style.SUCCESS('  ✓ Benutzer erstellt'))

    def create_auftraege(self):
        """Create test Aufträge with hierarchical structure"""
        today = datetime.now().date()

        # Create Aufträge
        auftraege_data = [
            {
                'auftragnamen': 'Nothilfe-Paket 1',
                'kategorie': 'Medizinische Ausrüstung',
                'verfallsdatum': today + timedelta(days=30),
            },
            {
                'auftragnamen': 'Nothilfe-Paket 2',
                'kategorie': 'Lebensmittel',
                'verfallsdatum': today + timedelta(days=60),
            },
            {
                'auftragnamen': 'Winterbedarf',
                'kategorie': 'Decken & Kleidung',
                'verfallsdatum': today + timedelta(days=90),
            },
            {
                'auftragnamen': 'Wasser & Hygiene',
                'kategorie': 'Verbrauchsmaterialien',
                'verfallsdatum': today + timedelta(days=45),
            },
        ]

        auftraege = {}
        for auftrag_data in auftraege_data:
            auftrag, _ = Auftrag.objects.get_or_create(**auftrag_data)
            auftraege[auftrag.auftrag_id] = auftrag

        # Create Container für Auftrag 1 (Medizinische Ausrüstung)
        container1_1 = Container.objects.create(
            auftrag=auftraege[1],
            container_name='Container A1',
            beschreibung='Medizinische Verbrauchsmaterialien'
        )
        container1_2 = Container.objects.create(
            auftrag=auftraege[1],
            container_name='Container A2',
            beschreibung='Instrumente und Geräte'
        )

        # Create Boxen für Container 1-1
        box1_1_1 = Box.objects.create(
            container=container1_1,
            box_name='Box 1',
            beschreibung='Verbandmaterial'
        )
        box1_1_2 = Box.objects.create(
            container=container1_1,
            box_name='Box 2',
            beschreibung='Desinfektionsmittel'
        )

        # Create Items für Boxen im Container 1-1
        Item.objects.create(box=box1_1_1, item_name='Verbandmaterial', menge=100)
        Item.objects.create(box=box1_1_1, item_name='Pflaster', menge=500)
        Item.objects.create(box=box1_1_2, item_name='Desinfektionsmittel', menge=50)
        Item.objects.create(box=box1_1_2, item_name='Handschuhe', menge=200)

        # Create Boxen für Container 1-2
        box1_2_1 = Box.objects.create(
            container=container1_2,
            box_name='Box 1',
            beschreibung='Thermometer und Stethoskope'
        )
        Item.objects.create(box=box1_2_1, item_name='Thermometer', menge=30)
        Item.objects.create(box=box1_2_1, item_name='Stethoskop', menge=15)

        # Create Container für Auftrag 2 (Lebensmittel)
        container2_1 = Container.objects.create(
            auftrag=auftraege[2],
            container_name='Container B1',
            beschreibung='Konserven und Haltbarware'
        )

        box2_1_1 = Box.objects.create(
            container=container2_1,
            box_name='Box 1',
            beschreibung='Konservendosen'
        )
        box2_1_2 = Box.objects.create(
            container=container2_1,
            box_name='Box 2',
            beschreibung='Trockenware'
        )

        Item.objects.create(box=box2_1_1, item_name='Konservenware', menge=500)
        Item.objects.create(box=box2_1_1, item_name='Gemüsekonserven', menge=300)
        Item.objects.create(box=box2_1_2, item_name='Reis', menge=100)
        Item.objects.create(box=box2_1_2, item_name='Nudeln', menge=150)

        # Create Container für Auftrag 3 (Winterbedarf)
        container3_1 = Container.objects.create(
            auftrag=auftraege[3],
            container_name='Container C1',
            beschreibung='Textilien'
        )

        box3_1_1 = Box.objects.create(
            container=container3_1,
            box_name='Box 1',
            beschreibung='Decken'
        )
        box3_1_2 = Box.objects.create(
            container=container3_1,
            box_name='Box 2',
            beschreibung='Winterkleidung'
        )

        Item.objects.create(box=box3_1_1, item_name='Wolldecken', menge=200)
        Item.objects.create(box=box3_1_2, item_name='Winterjacken', menge=80)
        Item.objects.create(box=box3_1_2, item_name='Handschuhe (Winter)', menge=120)

        # Create Container für Auftrag 4 (Wasser & Hygiene)
        container4_1 = Container.objects.create(
            auftrag=auftraege[4],
            container_name='Container D1',
            beschreibung='Wasserbehälter'
        )

        box4_1_1 = Box.objects.create(
            container=container4_1,
            box_name='Box 1',
            beschreibung='Trinkwasser'
        )
        box4_1_2 = Box.objects.create(
            container=container4_1,
            box_name='Box 2',
            beschreibung='Hygieneartikel'
        )

        Item.objects.create(box=box4_1_1, item_name='Trinkwasser', menge=75)
        Item.objects.create(box=box4_1_2, item_name='Seife', menge=200)
        Item.objects.create(box=box4_1_2, item_name='Zahnbürsten', menge=150)

        # Create ItemBestand (ungebundene Items)
        ItemBestand.objects.create(
            auftrag=auftraege[1],
            item_name='Einwegspritzen',
            gesamtmenge=500,
            beschreibung='Noch nicht in Boxen verpackt'
        )
        ItemBestand.objects.create(
            auftrag=auftraege[2],
            item_name='Energieriegel',
            gesamtmenge=1000,
            beschreibung='Im Lager vorrätig'
        )
        ItemBestand.objects.create(
            auftrag=auftraege[3],
            item_name='Socken',
            gesamtmenge=300,
            beschreibung='Noch zu verpacken'
        )

        # Create Prüfungen
        pruefung_status = Status.objects.get(name='Bestanden', typ='Pruefung')
        pruefer = User.objects.get(username='test_pruefer')

        for auftrag_id, auftrag in auftraege.items():
            pruefung, _ = Pruefung.objects.get_or_create(
                auftrag=auftrag,
                defaults={
                    'pruefer': pruefer,
                    'gesamtstatus': pruefung_status,
                }
            )

            # Create Prüfergebnisse für alle Items in allen Containern/Boxen
            for container in auftrag.container.all():
                for box in container.boxen.all():
                    for item in box.items.all():
                        position_status = Status.objects.get(name='Vollständig', typ='Position')
                        PruefErgebnis.objects.get_or_create(
                            pruefung=pruefung,
                            item=item,
                            defaults={
                                'status': position_status,
                                'bemerkung': 'Qualität geprüft und bestätigt',
                            }
                        )

        # Create Schwund entries
        schwund_status = Status.objects.get(name='Offen', typ='Auftrag')
        if list(auftraege.values()):
            schwund_auftrag = list(auftraege.values())[0]
            Schwund.objects.get_or_create(
                auftrag=schwund_auftrag,
                defaults={
                    'klassifizierung': 'Beschädigung',
                    'notiz': 'Verpackung beschädigt während Transport',
                    'pruefer': pruefer,
                    'status': schwund_status,
                }
            )

        self.stdout.write(self.style.SUCCESS('  ✓ Aufträge, Container, Boxen, Items und Prüfungen erstellt'))
