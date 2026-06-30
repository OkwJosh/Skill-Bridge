import os
import sys
import django
import random
import uuid
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
django.setup()

from django.db import transaction
from django.contrib.auth import get_user_model
from talents.models import TalentProfile, TalentSkill
from organizations.models import Organization, OrganizationMember
from mentors.models import MentorProfile
from opportunities.models import Opportunity, Application, OpportunityStatus, OpportunityType
from core.models import CanonicalSkill, Category
from faker import Faker

User = get_user_model()
fake = Faker()

TEST_PASSWORD = "TestPassword123!"

def generate_random_avatar(email):
    return f"https://api.dicebear.com/7.x/avataaars/png?seed={email}"

def generate_random_logo(company_name):
    encoded_name = company_name.replace(" ", "+")
    return f"https://ui-avatars.com/api/?name={encoded_name}&background=random&size=200"

def run_seed():
    print("=" * 80)
    print("CLEARING ENTIRE DATABASE")
    print("=" * 80)
    
    # 1. Clear Data
    User.objects.all().delete()
    Organization.objects.all().delete()
    Opportunity.objects.all().delete()
    Application.objects.all().delete()
    print("All users, organizations, opportunities, and applications deleted from Django DB.")

    # 2. Setup 1 Real Account for each role (Login-able)
    print("\n" + "=" * 80)
    print("SETTING UP REAL LOGIN-ABLE ACCOUNTS")
    print(f"Password for all core test accounts: {TEST_PASSWORD}")
    print("=" * 80)
    
    # Core Test Accounts
    core_users = [
        {"email": "talent@skillbridge.com", "role": "talent", "name": "Test Talent"},
        {"email": "orgadmin@skillbridge.com", "role": "org_admin", "name": "Test Org Admin"},
        {"email": "mentor@skillbridge.com", "role": "mentor", "name": "Test Mentor"}
    ]
    
    created_core_users = {}
    for cu in core_users:
        u = User.objects.create_user(
            username=cu["email"],
            email=cu["email"],
            password=TEST_PASSWORD,
            full_name=cu["name"],
            email_verified=True,
            avatar_url=generate_random_avatar(cu["email"]),
            supabase_uid=str(uuid.uuid4())
        )
        if cu["role"] == "talent":
            u.is_talent = True
            TalentProfile.objects.create(
                user=u,
                headline="Lead React Developer",
                bio="Experienced frontend developer looking for remote roles.",
                city="Lagos",
                country="Nigeria",
                is_available=True
            )
        elif cu["role"] == "org_admin":
            u.is_org_admin = True
        elif cu["role"] == "mentor":
            u.is_mentor = True
            MentorProfile.objects.create(
                user=u,
                headline="Senior Engineering Manager",
                bio="Mentoring junior devs to achieve their goals.",
                is_accepting_mentees=True,
                max_mentees=5
            )
        u.save()
        created_core_users[cu["role"]] = u
        print(f"Created {cu['role']}: {cu['email']}")

    # Setup core test organization for the orgadmin
    core_org = Organization.objects.create(
        name="SkillBridge Tech",
        slug="skillbridge-tech",
        description="A cool startup in Lagos.",
        website_url="https://skillbridge.local",
        city="Lagos",
        country="Nigeria",
        company_size="11-50",
        is_verified=True,
        logo_url=generate_random_logo("SkillBridge Tech")
    )
    OrganizationMember.objects.create(
        user=created_core_users["org_admin"],
        organization=core_org,
        role="admin"
    )
    print("Created test organization: SkillBridge Tech")

    print("\n" + "=" * 80)
    print("SEEDING MASSIVE DUMMY DATA")
    print("=" * 80)
    
    # Get base data
    skills = list(CanonicalSkill.objects.all())
    categories = list(Category.objects.all())
    
    # 3. Seed Organizations
    print("Generating 100 Organizations...")
    orgs = []
    with transaction.atomic():
        for i in range(100):
            company_name = fake.company()
            org = Organization(
                name=company_name,
                slug=fake.unique.slug(),
                description=fake.catch_phrase(),
                website_url=fake.url(),
                city=fake.city(),
                state=fake.state(),
                country=fake.country(),
                company_size=random.choice(['1-10', '11-50', '51-200', '201-500']),
                is_verified=random.choice([True, False]),
                logo_url=generate_random_logo(company_name)
            )
            orgs.append(org)
        Organization.objects.bulk_create(orgs)
        
    all_orgs = list(Organization.objects.all())

    # 4. Seed Talents (Users + Profiles)
    print("Generating 500 Talents...")
    talents = []
    users = []
    with transaction.atomic():
        for i in range(500):
            email = fake.unique.email()
            user = User(
                username=email,
                email=email,
                password="", # Dummy users can't login natively anyway
                full_name=fake.name(),
                is_talent=True,
                supabase_uid=str(uuid.uuid4()),
                avatar_url=generate_random_avatar(email),
                email_verified=True
            )
            users.append(user)
        User.objects.bulk_create(users)
        
    all_dummy_users = User.objects.filter(is_talent=True).exclude(email="talent@skillbridge.com")
    
    with transaction.atomic():
        for u in all_dummy_users:
            profile = TalentProfile(
                user=u,
                headline=fake.job(),
                bio=fake.text(max_nb_chars=200),
                education_route=random.choice(['university', 'bootcamp', 'self_taught']),
                city=fake.city(),
                state=fake.state(),
                country=fake.country(),
                is_available=random.choice([True, False, True, True])
            )
            talents.append(profile)
        TalentProfile.objects.bulk_create(talents)

    # 5. Seed Opportunities
    print("Generating 500 Opportunities...")
    opportunities = []
    with transaction.atomic():
        for i in range(500):
            org = random.choice(all_orgs)
            opp = Opportunity(
                organization=org,
                title=fake.job(),
                slug=fake.unique.slug(),
                description=fake.text(max_nb_chars=1000),
                category=random.choice(categories) if categories else None,
                opportunity_type=random.choice([OpportunityType.INTERNSHIP, OpportunityType.MICRO_PROJECT]),
                status=random.choice([OpportunityStatus.OPEN, OpportunityStatus.OPEN, OpportunityStatus.CLOSED]),
                experience_level=random.choice(['beginner', 'intermediate']),
                location=f"{org.city}, {org.country}",
                is_remote=random.choice([True, False])
            )
            opportunities.append(opp)
        Opportunity.objects.bulk_create(opportunities)
        
    all_opps = list(Opportunity.objects.filter(status=OpportunityStatus.OPEN))
    
    # 6. Seed Applications
    print("Generating 1500 Applications...")
    all_talent_profiles = list(TalentProfile.objects.all())
    applications = []
    
    with transaction.atomic():
        for i in range(1500):
            talent = random.choice(all_talent_profiles)
            opp = random.choice(all_opps)
            app = Application(
                opportunity=opp,
                talent=talent,
                status=random.choice(['pending', 'reviewing', 'shortlisted', 'accepted', 'rejected']),
                cover_letter=fake.text(max_nb_chars=300)
            )
            applications.append(app)
        
        # Avoid duplicate applications using ignore_conflicts
        Application.objects.bulk_create(applications, ignore_conflicts=True)

    print("=" * 80)
    print("SEEDING COMPLETE!")
    print(f"Total Users: {User.objects.count()}")
    print(f"Total Organizations: {Organization.objects.count()}")
    print(f"Total Opportunities: {Opportunity.objects.count()}")
    print(f"Total Applications: {Application.objects.count()}")
    print("=" * 80)

if __name__ == '__main__':
    run_seed()
