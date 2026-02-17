from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import connection
from datetime import datetime, timedelta
from core.models import Status
from auftraege.models import Auftrag, Items
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
            Items.objects.all().delete()
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
        """Create test Aufträge with items"""
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

        # Create Items entries
        items_data = [
            {'auftrag_id': 1, 'item_name': 'Verbandmaterial', 'menge': 100},
            {'auftrag_id': 1, 'item_name': 'Desinfektionsmittel', 'menge': 50},
            {'auftrag_id': 2, 'item_name': 'Konservenware', 'menge': 500},
            {'auftrag_id': 3, 'item_name': 'Wolldecken', 'menge': 200},
            {'auftrag_id': 4, 'item_name': 'Trinkwasser', 'menge': 75},
        ]

        items_dict = {}
        for item_data in items_data:
            if item_data['auftrag_id'] in auftraege:
                item, _ = Items.objects.get_or_create(
                    auftrag=auftraege[item_data['auftrag_id']],
                    item_name=item_data['item_name'],
                    defaults={'menge': item_data['menge']}
                )
                items_dict[item.item_id] = item

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

            # Create Prüfergebnisse
            for item in auftrag.items.all():
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

        self.stdout.write(self.style.SUCCESS('  ✓ Aufträge, Items und Prüfungen erstellt'))
