"""
Create Test Opportunities and Applications
==========================================
Creates sample opportunities and applications for testing.

Usage:
    python create_test_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from core.models import CanonicalSkill
from talents.models import TalentProfile, TalentSkill
from organizations.models import Organization, OrganizationMember
from mentors.models import MentorProfile
from opportunities.models import Opportunity, Application

User = get_user_model()

print("=" * 80)
print("🚀 CREATING TEST OPPORTUNITIES & APPLICATIONS")
print("=" * 80)

# =============================================================================
# GET EXISTING USERS
# =============================================================================

print("\n📋 Finding users...")

try:
    talent_user = User.objects.filter(is_talent=True).first()
    org_user = User.objects.filter(is_org_admin=True).first()
    mentor_user = User.objects.filter(is_mentor=True).first()
    
    if not talent_user:
        print("❌ No talent user found. Run create_linked_users.py first.")
        exit(1)
    if not org_user:
        print("❌ No org admin user found. Run create_linked_users.py first.")
        exit(1)
    if not mentor_user:
        print("❌ No mentor user found. Run create_linked_users.py first.")
        exit(1)
        
    print(f"   ✅ Talent: {talent_user.email}")
    print(f"   ✅ Org Admin: {org_user.email}")
    print(f"   ✅ Mentor: {mentor_user.email}")
    
except Exception as e:
    print(f"❌ Error finding users: {e}")
    exit(1)

# =============================================================================
# GET RELATED OBJECTS
# =============================================================================

print("\n📋 Finding related objects...")

# Get org membership
org_membership = OrganizationMember.objects.filter(user=org_user).first()
if not org_membership:
    print("❌ Org admin not linked to organization. Run create_linked_users.py first.")
    exit(1)
org = org_membership.organization
print(f"   ✅ Organization: {org.name}")

# Get mentor profile
mentor_profile = MentorProfile.objects.filter(user=mentor_user).first()
if not mentor_profile:
    print("❌ Mentor profile not found. Run create_linked_users.py first.")
    exit(1)
print(f"   ✅ Mentor Profile: {mentor_profile.headline}")

# Get or create talent profile
talent_profile, _ = TalentProfile.objects.get_or_create(
    user=talent_user,
    defaults={
        'headline': 'Full Stack Developer',
        'bio': 'Looking for opportunities',
        'education_route': 'university',
        'city': 'Lagos',
        'is_available': True,
    }
)
print(f"   ✅ Talent Profile: {talent_profile.headline}")

# Get skills
skills = list(CanonicalSkill.objects.all()[:5])
if not skills:
    print("❌ No skills found. Run seed_data command first.")
    exit(1)
print(f"   ✅ Skills: {[s.name for s in skills]}")

# =============================================================================
# ADD SKILLS TO TALENT PROFILE
# =============================================================================

print("\n🎯 Adding skills to talent profile...")

for skill in skills[:3]:  # Add first 3 skills
    talent_skill, created = TalentSkill.objects.get_or_create(
        talent=talent_profile,
        skill=skill,
        defaults={
            'proficiency': 'intermediate',
            'years_experience': 2,
        }
    )
    if created:
        print(f"   ✅ Added skill: {skill.name}")
    else:
        print(f"   ⏭️  Skill exists: {skill.name}")

# =============================================================================
# CREATE OPPORTUNITIES
# =============================================================================

print("\n💼 Creating opportunities...")

from django.utils.text import slugify

# Opportunity 1: Posted by Organization
opp1, created = Opportunity.objects.get_or_create(
    title='Backend Developer Internship',
    organization=org,
    defaults={
        'slug': slugify('Backend Developer Internship'),
        'created_by': org_user,
        'description': '''We are looking for talented Python/Django developers to join our team.

Responsibilities:
- Build RESTful APIs using Django REST Framework
- Write clean, maintainable code
- Collaborate with frontend developers
- Participate in code reviews

Requirements:
- Knowledge of Python and Django
- Understanding of REST APIs
- Familiarity with PostgreSQL
- Good communication skills''',
        'opportunity_type': 'internship',
        'experience_level': 'Entry-level',
        'is_remote': True,
        'location': 'Lagos, Nigeria',
        'is_paid': True,
        'compensation': '₦150,000/month',
        'duration': '3 months',
        'spots_available': 2,
        'max_applicants': 50,
        'application_deadline': timezone.now() + timedelta(days=30),
        'start_date': timezone.now().date() + timedelta(days=45),
        'status': 'open',
    }
)
if created:
    opp1.required_skills.set(skills[:3])
    print(f"   ✅ Created: {opp1.title} (ID: {opp1.id})")
    print(f"      Posted by: {org.name}")
else:
    print(f"   ⏭️  Exists: {opp1.title} (ID: {opp1.id})")

# Opportunity 2: Posted by Mentor (Guided Project)
opp2, created = Opportunity.objects.get_or_create(
    title='Build a REST API - Guided Project',
    mentor=mentor_profile,
    defaults={
        'slug': slugify('Build a REST API - Guided Project'),
        'created_by': mentor_user,
        'description': '''Learn to build production-ready REST APIs with Django REST Framework.

What you'll learn:
- Django project structure
- DRF serializers and views
- JWT authentication
- API documentation with Swagger
- Deployment to Railway

This is a 4-week guided project with weekly sessions.''',
        'opportunity_type': 'guided_project',
        'experience_level': 'Beginner to Intermediate',
        'is_remote': True,
        'location': 'Online',
        'is_paid': False,
        'duration': '4 weeks',
        'spots_available': 10,
        'max_applicants': 30,
        'application_deadline': timezone.now() + timedelta(days=14),
        'start_date': timezone.now().date() + timedelta(days=21),
        'status': 'open',
    }
)
if created:
    opp2.required_skills.set([skills[0]])  # Just Python
    print(f"   ✅ Created: {opp2.title} (ID: {opp2.id})")
    print(f"      Posted by: {mentor_user.email}")
else:
    print(f"   ⏭️  Exists: {opp2.title} (ID: {opp2.id})")

# Opportunity 3: Another org opportunity
opp3, created = Opportunity.objects.get_or_create(
    title='Frontend Developer - React',
    organization=org,
    defaults={
        'slug': slugify('Frontend Developer - React'),
        'created_by': org_user,
        'description': '''Join our team as a React developer.

We're building a next-gen fintech platform and need passionate developers.

Tech stack: React, TypeScript, Node.js''',
        'opportunity_type': 'internship',
        'experience_level': 'Intermediate',
        'is_remote': False,
        'location': 'Lagos Island, Lagos',
        'is_paid': True,
        'compensation': '₦200,000/month',
        'duration': '6 months',
        'spots_available': 1,
        'max_applicants': 30,
        'application_deadline': timezone.now() + timedelta(days=21),
        'start_date': timezone.now().date() + timedelta(days=30),
        'status': 'open',
    }
)
if created:
    react_skill = CanonicalSkill.objects.filter(name='React').first()
    js_skill = CanonicalSkill.objects.filter(name='JavaScript').first()
    if react_skill and js_skill:
        opp3.required_skills.set([react_skill, js_skill])
    print(f"   ✅ Created: {opp3.title} (ID: {opp3.id})")
else:
    print(f"   ⏭️  Exists: {opp3.title} (ID: {opp3.id})")

# =============================================================================
# CREATE APPLICATIONS
# =============================================================================

print("\n📝 Creating applications from talent...")

# Application 1: To org's opportunity
app1, created = Application.objects.get_or_create(
    opportunity=opp1,
    talent=talent_profile,
    defaults={
        'cover_letter': '''Dear Hiring Manager,

I am excited to apply for the Backend Developer Internship at Acme Tech.

With 2 years of experience in Python and Django, I have built several REST APIs and am familiar with PostgreSQL. I am eager to learn from your team and contribute to your projects.

Best regards,
Test Talent''',
        'status': 'pending',
    }
)
if created:
    print(f"   ✅ Created application for: {opp1.title}")
    print(f"      Application ID: {app1.id}")
    print(f"      Status: {app1.status}")
else:
    print(f"   ⏭️  Application exists (ID: {app1.id})")

# Application 2: To mentor's guided project
app2, created = Application.objects.get_or_create(
    opportunity=opp2,
    talent=talent_profile,
    defaults={
        'cover_letter': '''Hi,

I would love to join your guided project to learn more about building REST APIs with Django.

I have basic Python knowledge and am eager to level up my backend skills.

Thanks!''',
        'status': 'pending',
    }
)
if created:
    print(f"   ✅ Created application for: {opp2.title}")
    print(f"      Application ID: {app2.id}")
    print(f"      Status: {app2.status}")
else:
    print(f"   ⏭️  Application exists (ID: {app2.id})")

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 80)
print("✅ TEST DATA CREATED SUCCESSFULLY!")
print("=" * 80)

print("\n📋 OPPORTUNITIES:")
for opp in Opportunity.objects.all():
    owner = opp.organization or opp.mentor
    print(f"   ID: {opp.id} | {opp.title}")
    print(f"      Type: {opp.opportunity_type} | Owner: {owner}")
    print()

print("\n📋 APPLICATIONS:")
for app in Application.objects.all():
    print(f"   ID: {app.id} | {app.opportunity.title}")
    print(f"      Applicant: {app.talent.user.email}")
    print(f"      Status: {app.status}")
    print()

print("\n🧪 TESTING GUIDE:")
print("-" * 60)
print("""
1. AS ORG ADMIN (orgadmin@skillbridge.com):
   - GET  /api/v1/opportunities/          → See all opportunities
   - POST /api/v1/opportunities/          → Create new opportunity
   - GET  /api/v1/opportunities/1/        → View opportunity 1 (yours)
   - PATCH /api/v1/opportunities/1/       → Update opportunity 1 (yours)
   - GET  /api/v1/opportunities/1/applications/  → View applications
   - PATCH /api/v1/opportunities/applications/1/status/  → Update app status

2. AS MENTOR (mentor@skillbridge.com):
   - GET  /api/v1/opportunities/2/        → View opportunity 2 (yours)
   - PATCH /api/v1/opportunities/2/       → Update opportunity 2 (yours)
   - GET  /api/v1/opportunities/2/applications/  → View applications

3. AS TALENT (talent@skillbridge.com):
   - GET  /api/v1/opportunities/          → Browse opportunities
   - POST /api/v1/opportunities/3/apply/  → Apply to opportunity 3
   - GET  /api/v1/opportunities/my-applications/  → View my applications
""")
print("=" * 80)
