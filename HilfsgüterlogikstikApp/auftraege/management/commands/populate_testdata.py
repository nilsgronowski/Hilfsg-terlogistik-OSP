from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.db import connection
from datetime import datetime, timedelta
from auftraege.models import Order, Container, Box, Item
from pruefung.models import OrderInspection, IndividualInspection, InspectionResult, Shrinkage


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
        self.create_orders()

        self.stdout.write(self.style.SUCCESS('✅ Test data successfully created!'))

    def clear_data(self):
        """Delete existing test data with FK constraint handling"""
        # Disable foreign key checks for MySQL
        with connection.cursor() as cursor:
            cursor.execute('SET FOREIGN_KEY_CHECKS=0')
        
        try:
            # Delete all test data
            Shrinkage.objects.all().delete()
            InspectionResult.objects.all().delete()
            IndividualInspection.objects.all().delete()
            OrderInspection.objects.all().delete()
            Item.objects.all().delete()
            Box.objects.all().delete()
            Container.objects.all().delete()
            Order.objects.all().delete()
            
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

    def create_orders(self):
        """Create test orders with hierarchical structure"""
        today = datetime.now().date()

        # Create Orders
        orders_data = [
            {
                'name': 'Emergency Package 1',
                'category': 'Medical Equipment',
                'expiry_date': today + timedelta(days=30),
            },
            {
                'name': 'Emergency Package 2',
                'category': 'Food',
                'expiry_date': today + timedelta(days=60),
            },
            {
                'name': 'Winter Supplies',
                'category': 'Blankets & Clothing',
                'expiry_date': today + timedelta(days=90),
            },
            {
                'name': 'Water & Hygiene',
                'category': 'Consumables',
                'expiry_date': today + timedelta(days=45),
            },
        ]

        orders = {}
        for order_data in orders_data:
            order, _ = Order.objects.get_or_create(**order_data)
            orders[order.order_id] = order

        # Create Container for Order 1 (Medical Equipment)
        container1_1 = Container.objects.create(
            order=orders[1],
            name='Container A1',
            description='Medical consumables'
        )
        container1_2 = Container.objects.create(
            order=orders[1],
            name='Container A2',
            description='Instruments and devices'
        )

        # Create Boxes for Container 1-1
        box1_1_1 = Box.objects.create(
            container=container1_1,
            name='Box 1',
            description='Dressing material'
        )
        box1_1_2 = Box.objects.create(
            container=container1_1,
            name='Box 2',
            description='Disinfectants'
        )

        # Create Items for Boxes in Container 1-1
        Item.objects.create(box=box1_1_1, name='Dressing material', quantity=100)
        Item.objects.create(box=box1_1_1, name='Bandages', quantity=500)
        Item.objects.create(box=box1_1_2, name='Disinfectant', quantity=50)
        Item.objects.create(box=box1_1_2, name='Gloves', quantity=200)

        # Create Boxes for Container 1-2
        box1_2_1 = Box.objects.create(
            container=container1_2,
            name='Box 1',
            description='Thermometers and stethoscopes'
        )
        Item.objects.create(box=box1_2_1, name='Thermometer', quantity=30)
        Item.objects.create(box=box1_2_1, name='Stethoscope', quantity=15)

        # Create Container for Order 2 (Food)
        container2_1 = Container.objects.create(
            order=orders[2],
            name='Container B1',
            description='Canned and shelf-stable goods'
        )

        box2_1_1 = Box.objects.create(
            container=container2_1,
            name='Box 1',
            description='Canned food'
        )
        box2_1_2 = Box.objects.create(
            container=container2_1,
            name='Box 2',
            description='Dry goods'
        )

        Item.objects.create(box=box2_1_1, name='Canned goods', quantity=500)
        Item.objects.create(box=box2_1_1, name='Canned vegetables', quantity=300)
        Item.objects.create(box=box2_1_2, name='Rice', quantity=100)
        Item.objects.create(box=box2_1_2, name='Pasta', quantity=150)

        # Create Container for Order 3 (Winter Supplies)
        container3_1 = Container.objects.create(
            order=orders[3],
            name='Container C1',
            description='Textiles'
        )

        box3_1_1 = Box.objects.create(
            container=container3_1,
            name='Box 1',
            description='Blankets'
        )
        box3_1_2 = Box.objects.create(
            container=container3_1,
            name='Box 2',
            description='Winter clothing'
        )

        Item.objects.create(box=box3_1_1, name='Wool blankets', quantity=200)
        Item.objects.create(box=box3_1_2, name='Winter jackets', quantity=80)
        Item.objects.create(box=box3_1_2, name='Gloves (winter)', quantity=120)

        # Create Container for Order 4 (Water & Hygiene)
        container4_1 = Container.objects.create(
            order=orders[4],
            name='Container D1',
            description='Water containers'
        )

        box4_1_1 = Box.objects.create(
            container=container4_1,
            name='Box 1',
            description='Drinking water'
        )
        box4_1_2 = Box.objects.create(
            container=container4_1,
            name='Box 2',
            description='Hygiene articles'
        )

        Item.objects.create(box=box4_1_1, name='Drinking water', quantity=75)
        Item.objects.create(box=box4_1_2, name='Soap', quantity=200)
        Item.objects.create(box=box4_1_2, name='Toothbrushes', quantity=150)

        # Create Order Inspections
        inspector = User.objects.get(username='test_inspector')

        for order_id, order in orders.items():
            # Create Order Inspection
            order_inspection, _ = OrderInspection.objects.get_or_create(
                order=order,
                defaults={
                    'inspector': inspector,
                    'overall_status': OrderInspection.InspectionStatus.BESTANDEN,
                }
            )

            # Create Individual Inspections for each Container
            for container in order.containers.all():
                individual_inspection, _ = IndividualInspection.objects.get_or_create(
                    order_inspection=order_inspection,
                    container=container,
                    defaults={
                        'inspector': inspector,
                        'status': IndividualInspection.IndividualInspectionStatus.VOLLSTAENDIG,
                        'comment': f'Inspection of {container.name}',
                    }
                )

                # Create Inspection Results for all Items in all Boxes of this Container
                for box in container.boxes.all():
                    for item in box.items.all():
                        InspectionResult.objects.get_or_create(
                            individual_inspection=individual_inspection,
                            item=item,
                            defaults={
                                'status': InspectionResult.ResultStatus.VOLLSTAENDIG,
                                'comment': 'Quality checked and confirmed',
                            }
                        )

            # Create Shrinkage Report for the first Order Inspection
            if order_id == 1:
                Shrinkage.objects.get_or_create(
                    order_inspection=order_inspection,
                    defaults={
                        'classification': 'Damage',
                        'note': 'Packaging damaged during transport',
                        'created_by': inspector,
                        'status': Shrinkage.ShrinkageStatus.GEMELDET,
                    }
                )

        self.stdout.write(self.style.SUCCESS('  ✓ Orders, Containers, Boxes, Items and Inspections created'))
