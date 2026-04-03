import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from talents.models import TalentProfile
from organizations.models import Organization, OrganizationMember
from mentors.models import MentorProfile
from schools.models import School
from core.models import CanonicalIndustry

User = get_user_model()

print("=" * 80)
print("🔧 SETTING UP ALL ROLES")
print("=" * 80)

# 1. TALENT USER
talent_user = User.objects.get(email='talent@test.com')
talent_user.is_talent = True
talent_user.is_org_admin = False
talent_user.is_mentor = False
talent_user.is_school_admin = False
talent_user.save()
print(f"✅ {talent_user.email} - is_talent=True")

# Create talent profile if missing
TalentProfile.objects.get_or_create(
    user=talent_user,
    defaults={
        'headline': 'Full Stack Developer',
        'bio': 'Test talent profile',
        'education_route': 'university',
        'city': 'Lagos',
        'is_available': True,
    }
)
print(f"   ✅ TalentProfile created")

# 2. ORG ADMIN USER
org_user = User.objects.get(email='orgadmin@test.com')
org_user.is_talent = False
org_user.is_org_admin = True
org_user.is_mentor = False
org_user.is_school_admin = False
org_user.save()
print(f"✅ {org_user.email} - is_org_admin=True")

# Link to organization
tech_industry = CanonicalIndustry.objects.get(name='Technology')
org, _ = Organization.objects.get_or_create(
    name='Acme Tech',
    defaults={
        'slug': 'acme-tech',
        'industry': tech_industry,
        'city': 'Lagos',
    }
)
OrganizationMember.objects.get_or_create(
    user=org_user,
    organization=org,
    defaults={'role': 'owner'}
)
print(f"   ✅ OrganizationMember linked to Acme Tech")

# 3. MENTOR USER
mentor_user = User.objects.get(email='mentor@test.com')
mentor_user.is_talent = False
mentor_user.is_org_admin = False
mentor_user.is_mentor = True
mentor_user.is_school_admin = False
mentor_user.save()
print(f"✅ {mentor_user.email} - is_mentor=True")

# Create mentor profile if missing
MentorProfile.objects.get_or_create(
    user=mentor_user,
    defaults={
        'headline': 'Senior Developer',
        'bio': 'Test mentor profile',
        'is_accepting_mentees': True,
    }
)
print(f"   ✅ MentorProfile created")

# 4. SCHOOL ADMIN USER
school_user = User.objects.get(email='schooladmin@test.com')
school_user.is_talent = False
school_user.is_org_admin = False
school_user.is_mentor = False
school_user.is_school_admin = True
school_user.save()
print(f"✅ {school_user.email} - is_school_admin=True")

# Link to school
school = School.objects.get(name='University of Lagos')
school.admins.add(school_user)
print(f"   ✅ Linked to University of Lagos")

# 5. MULTI-ROLE USER
multi_user = User.objects.get(email='multi@test.com')
multi_user.is_talent = True
multi_user.is_org_admin = False
multi_user.is_mentor = True
multi_user.is_school_admin = False
multi_user.save()
print(f"✅ {multi_user.email} - is_talent=True, is_mentor=True")

TalentProfile.objects.get_or_create(user=multi_user, defaults={'headline': 'Multi-role user'})
MentorProfile.objects.get_or_create(user=multi_user, defaults={'headline': 'Multi-role mentor'})
print(f"   ✅ Profiles created")

print("\n" + "=" * 80)
print("✅ ALL ROLES CONFIGURED SUCCESSFULLY!")
print("=" * 80)