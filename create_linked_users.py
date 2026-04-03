"""
Create Django Users Linked to Supabase
======================================
Run after creating users in Supabase.

Usage:
    python create_linked_users.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils.text import slugify
from core.models import CanonicalSkill, CanonicalIndustry
from talents.models import TalentProfile
from organizations.models import Organization, OrganizationMember
from mentors.models import MentorProfile
from schools.models import School, StudentRosterRecord

User = get_user_model()

print("=" * 80)
print("🔗 CREATE DJANGO USERS LINKED TO SUPABASE")
print("=" * 80)

# =============================================================================
# PASTE YOUR SUPABASE UIDs HERE (from Step 2)
# =============================================================================

SUPABASE_USERS = {
    'talent@skillbridge.com': {
        'uid': '0709065d-09dd-4abb-8f30-4f6ccd742295',  # <-- Replace with actual UID
        'full_name': 'Test Talent',
        'is_talent': True,
        'is_org_admin': False,
        'is_mentor': False,
        'is_school_admin': False,
    },
    'orgadmin@skillbridge.com': {
        'uid': '45e33dda-675e-4ff0-94c6-e2592ce14a5a',  # <-- Replace with actual UID
        'full_name': 'Test Org Admin',
        'is_talent': False,
        'is_org_admin': True,
        'is_mentor': False,
        'is_school_admin': False,
    },
    'mentor@skillbridge.com': {
        'uid': '651592d5-7ea3-47df-be8f-d332a8503b7d',  # <-- Replace with actual UID
        'full_name': 'Test Mentor',
        'is_talent': False,
        'is_org_admin': False,
        'is_mentor': True,
        'is_school_admin': False,
    },
    'schooladmin@skillbridge.com': {
        'uid': '506e6f29-2c89-460e-89fd-3c10d903ef27',  # <-- Replace with actual UID
        'full_name': 'Test School Admin',
        'is_talent': False,
        'is_org_admin': False,
        'is_mentor': False,
        'is_school_admin': True,
    },
    'multi@skillbridge.com': {
        'uid': 'e5d09dc2-1e40-40cf-8aeb-42de70bdd574',  # <-- Replace with actual UID
        'full_name': 'Multi Role User',
        'is_talent': True,
        'is_org_admin': False,
        'is_mentor': True,
        'is_school_admin': False,
    },
}

# =============================================================================
# CREATE SEED DATA FIRST (Skills, Industries, etc.)
# =============================================================================

print("\n📦 Creating seed data...")

# Skills
skills_data = [
    ('Python', 'Backend'),
    ('JavaScript', 'Frontend'),
    ('React', 'Frontend'),
    ('Django', 'Backend'),
    ('PostgreSQL', 'Database'),
    ('Node.js', 'Backend'),
    ('TypeScript', 'Frontend'),
    ('AWS', 'DevOps'),
    ('Docker', 'DevOps'),
    ('Machine Learning', 'Data Science'),
]
for name, category in skills_data:
    CanonicalSkill.objects.get_or_create(
        name=name,
        defaults={'slug': slugify(name), 'category': category}
    )
print(f"   ✅ Skills: {CanonicalSkill.objects.count()}")

# Industries
industries = ['Technology', 'Finance', 'Healthcare', 'Education', 'E-commerce', 'Logistics', 'Agriculture', 'Energy']
for name in industries:
    CanonicalIndustry.objects.get_or_create(
        name=name,
        defaults={'slug': slugify(name)}
    )
print(f"   ✅ Industries: {CanonicalIndustry.objects.count()}")

# Organization
tech_industry = CanonicalIndustry.objects.get(name='Technology')
org, _ = Organization.objects.get_or_create(
    name='Acme Tech',
    defaults={
        'slug': 'acme-tech',
        'description': 'Leading tech company in Nigeria',
        'industry': tech_industry,
        'city': 'Lagos',
        'state': 'Lagos State',
        'country': 'Nigeria',
        'is_verified': True,
    }
)
print(f"   ✅ Organization: {org.name}")

# School
school, _ = School.objects.get_or_create(
    name='University of Lagos',
    defaults={
        'slug': 'university-of-lagos',
        'school_type': 'university',
        'city': 'Lagos',
        'state': 'Lagos State',
        'country': 'Nigeria',
        'is_verified': True,
    }
)
print(f"   ✅ School: {school.name}")

# Student Roster Record (for verification testing)
StudentRosterRecord.objects.get_or_create(
    school=school,
    matriculation_number='MAT2020001',
    defaults={
        'email': 'student@unilag.edu.ng',
        'full_name': 'Chioma Okafor',
        'department': 'Computer Science',
        'course_of_study': 'BSc Computer Science',
        'enrollment_year': 2020,
        'expected_graduation_year': 2024,
    }
)
print(f"   ✅ Student Roster Record: MAT2020001")

# =============================================================================
# CREATE DJANGO USERS
# =============================================================================

print("\n👤 Creating Django users linked to Supabase...")

for email, config in SUPABASE_USERS.items():
    # Skip if UID not set
    if config['uid'].startswith('PASTE_'):
        print(f"   ⚠️  Skipping {email} - UID not set")
        continue
    
    # Create or update user
    user, created = User.objects.update_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0],
            'supabase_uid': config['uid'],
            'full_name': config['full_name'],
            'is_talent': config['is_talent'],
            'is_org_admin': config['is_org_admin'],
            'is_mentor': config['is_mentor'],
            'is_school_admin': config['is_school_admin'],
        }
    )
    
    action = "Created" if created else "Updated"
    print(f"   ✅ {action}: {email}")
    print(f"      UID: {config['uid']}")
    
    # Create related profiles based on roles
    
    # Talent Profile
    if config['is_talent']:
        TalentProfile.objects.get_or_create(
            user=user,
            defaults={
                'headline': 'Full Stack Developer',
                'bio': 'Passionate developer looking for opportunities',
                'education_route': 'university',
                'institution_name': 'University of Lagos',
                'city': 'Lagos',
                'is_available': True,
            }
        )
        print(f"      → TalentProfile created")
    
    # Organization Membership
    if config['is_org_admin']:
        OrganizationMember.objects.get_or_create(
            user=user,
            organization=org,
            defaults={'role': 'owner'}
        )
        print(f"      → OrganizationMember linked to {org.name}")
    
    # Mentor Profile
    if config['is_mentor']:
        MentorProfile.objects.get_or_create(
            user=user,
            defaults={
                'headline': 'Senior Software Architect',
                'bio': '15+ years experience in building scalable systems',
                'is_accepting_mentees': True,
                'max_mentees': 5,
            }
        )
        print(f"      → MentorProfile created")
    
    # School Admin
    if config['is_school_admin']:
        school.admins.add(user)
        print(f"      → Linked to {school.name}")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("✅ SETUP COMPLETE!")
print("=" * 80)

print("\n📋 Test Accounts (Password: Test@123456):")
print("-" * 60)
for email, config in SUPABASE_USERS.items():
    roles = []
    if config['is_talent']: roles.append('talent')
    if config['is_org_admin']: roles.append('org_admin')
    if config['is_mentor']: roles.append('mentor')
    if config['is_school_admin']: roles.append('school_admin')
    print(f"   {email}")
    print(f"   Roles: {', '.join(roles)}")
    print()

print("\n🔐 Login via Supabase Auth to get JWT token")
print("   Then use token in Postman: Authorization: Bearer <token>")
print("=" * 80)
