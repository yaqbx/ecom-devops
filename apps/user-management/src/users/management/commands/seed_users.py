"""
Management command to seed the database with realistic user data.
Usage: python manage.py seed_users [--count 15]
"""
from django.core.management.base import BaseCommand, CommandParser
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

User = get_user_model()

ADMINS = [
    {
        "email": "admin@ecomdevops.com",
        "first_name": "Platform",
        "last_name": "Admin",
        "role": "admin",
        "status": "active",
        "is_staff": True,
        "is_superuser": True,
        "email_verified": True,
        "phone_verified": True,
        "identity_verified": True,
        "job_title": "System Administrator",
        "department": "IT",
        "city": "Warsaw",
        "country": "Poland",
        "language": "en",
    },
]

COMPANY_ADMINS = [
    {
        "email": "k.nowak@budex.pl",
        "first_name": "Krzysztof",
        "last_name": "Nowak",
        "role": "company_admin",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": True,
        "identity_verified": True,
        "job_title": "Dyrektor Techniczny",
        "department": "Zarzad",
        "city": "Krakow",
        "country": "Poland",
        "phone": "+48 601 111 222",
    },
    {
        "email": "m.wisniewski@polbud.com.pl",
        "first_name": "Marcin",
        "last_name": "Wisniewski",
        "role": "company_admin",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": True,
        "identity_verified": True,
        "job_title": "Project Manager",
        "department": "Operations",
        "city": "Wroclaw",
        "country": "Poland",
        "phone": "+48 602 333 444",
    },
    {
        "email": "a.kwiatkowska@infrapro.pl",
        "first_name": "Agnieszka",
        "last_name": "Kwiatkowska",
        "role": "company_admin",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": True,
        "identity_verified": True,
        "job_title": "Kierownik Budowy",
        "department": "Budowa",
        "city": "Gdansk",
        "country": "Poland",
        "phone": "+48 603 555 666",
    },
]

COMPANY_MANAGERS = [
    {
        "email": "p.kowalski@budex.pl",
        "first_name": "Piotr",
        "last_name": "Kowalski",
        "role": "company_manager",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": False,
        "identity_verified": True,
        "job_title": "Kierownik Robót",
        "department": "Budowa",
        "city": "Krakow",
        "country": "Poland",
        "phone": "+48 604 777 888",
    },
    {
        "email": "t.adamczyk@polbud.com.pl",
        "first_name": "Tomasz",
        "last_name": "Adamczyk",
        "role": "company_manager",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": True,
        "email_verified": False,
        "job_title": "Brygadzista",
        "department": "Produkcja",
        "city": "Wroclaw",
        "country": "Poland",
    },
]

COMPANY_OPERATORS = [
    {
        "email": "j.mazur@budex.pl",
        "first_name": "Jan",
        "last_name": "Mazur",
        "role": "company_operator",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": False,
        "job_title": "Operator Koparki",
        "department": "Sprzet",
        "city": "Katowice",
        "country": "Poland",
        "phone": "+48 605 111 222",
    },
    {
        "email": "r.krawczyk@polbud.com.pl",
        "first_name": "Robert",
        "last_name": "Krawczyk",
        "role": "company_operator",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": True,
        "job_title": "Operator Spycharki",
        "department": "Sprzet",
        "city": "Poznan",
        "country": "Poland",
    },
    {
        "email": "m.zielinski@infrapro.pl",
        "first_name": "Michal",
        "last_name": "Zielinski",
        "role": "company_operator",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": False,
        "job_title": "Operator Zurawia",
        "department": "Sprzet",
        "city": "Warsaw",
        "country": "Poland",
        "phone": "+48 606 333 444",
    },
    {
        "email": "d.wozniak@budex.pl",
        "first_name": "Dawid",
        "last_name": "Wozniak",
        "role": "company_operator",
        "status": "suspended",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": False,
        "job_title": "Operator Koparki",
        "department": "Sprzet",
        "city": "Lodz",
        "country": "Poland",
    },
]

CUSTOMERS = [
    {
        "email": "anna.jankowska@gmail.com",
        "first_name": "Anna",
        "last_name": "Jankowska",
        "role": "customer",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": True,
        "identity_verified": True,
        "job_title": "Wlasiciel Gospodarstwa",
        "city": "Lublin",
        "country": "Poland",
        "phone": "+48 607 555 666",
    },
    {
        "email": "tomaszbaran@wp.pl",
        "first_name": "Tomasz",
        "last_name": "Baran",
        "role": "customer",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": True,
        "job_title": "Rolnik",
        "city": "Rzeszow",
        "country": "Poland",
        "phone": "+48 608 777 888",
    },
    {
        "email": "kamil.szewczyk@onet.pl",
        "first_name": "Kamil",
        "last_name": "Szewczyk",
        "role": "customer",
        "status": "pending_verification",
        "is_staff": False,
        "email_verified": False,
        "phone_verified": False,
        "identity_verified": False,
        "city": "Bydgoszcz",
        "country": "Poland",
    },
    {
        "email": "piotr79@interia.pl",
        "first_name": "Piotr",
        "last_name": "Michalski",
        "role": "customer",
        "status": "inactive",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": False,
        "job_title": "Inzynier Budowlany",
        "city": "Szczecin",
        "country": "Poland",
    },
    {
        "email": "marek.kaminski@gmail.com",
        "first_name": "Marek",
        "last_name": "Kaminski",
        "role": "customer",
        "status": "active",
        "is_staff": False,
        "email_verified": True,
        "phone_verified": True,
        "identity_verified": True,
        "job_title": "Construction Contractor",
        "city": "Warsaw",
        "country": "Poland",
        "phone": "+48 609 111 222",
    },
]

ALL_USERS = ADMINS + COMPANY_ADMINS + COMPANY_MANAGERS + COMPANY_OPERATORS + CUSTOMERS


class Command(BaseCommand):
    help = "Seed database with realistic test users"

    def add_arguments(self, parser: CommandParser):
        parser.add_argument("--password", type=str, default="Test1234!")

    def handle(self, *args, **options):
        password = options["password"]
        created_count = 0
        skipped_count = 0

        for user_data in ALL_USERS:
            email = user_data["email"]
            if User.objects.filter(email=email).exists():
                self.stdout.write(self.style.WARNING(f"Skipping existing user: {email}"))
                skipped_count += 1
                continue

            user = User(
                email=email,
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data.get("role", "customer"),
                status=user_data.get("status", "pending_verification"),
                is_staff=user_data.get("is_staff", False),
                is_superuser=user_data.get("is_superuser", False),
                is_active=user_data.get("status", "active") != "inactive",
                email_verified=user_data.get("email_verified", False),
                phone_verified=user_data.get("phone_verified", False),
                identity_verified=user_data.get("identity_verified", False),
                job_title=user_data.get("job_title", ""),
                department=user_data.get("department", ""),
                city=user_data.get("city", ""),
                country=user_data.get("country", "Poland"),
                phone=user_data.get("phone", ""),
                date_joined=timezone.now() - timedelta(days=random.randint(1, 365)),
            )
            user.set_password(password)
            user.save()
            created_count += 1

            role_display = dict(User.ROLE_CHOICES).get(user.role, user.role)
            status_display = dict(User.STATUS_CHOICES).get(user.status, user.status)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Created {email} [{role_display}] ({status_display})"
                )
            )

        self.stdout.write()
        self.stdout.write(self.style.SUCCESS(f"Done. Created: {created_count}, Skipped: {skipped_count}, Total: {len(ALL_USERS)}"))
