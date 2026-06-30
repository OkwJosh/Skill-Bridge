
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from talents.models import TalentProfile
from organizations.models import Organization
from opportunities.models import Opportunity, Application, OpportunityType, OpportunityStatus, ApplicationStatus
from django.utils.text import slugify

User = get_user_model()

def main():
    # 1. Jason Dru
    email = 'jason.dru@example.com'
    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email,
            'full_name': 'Jason Dru',
            'is_talent': True
        }
    )
    if created:
        user.set_password('password123')
        user.save()
        print(f'Created user: {user.full_name}')
    else:
        print(f'Found user: {user.full_name}')

    talent_profile, created = TalentProfile.objects.get_or_create(
        user=user,
        defaults={'headline': 'Mobile Developer'}
    )

    # 2. Derrick Ventures
    org_name = 'Derrick Ventures'
    org_slug = slugify(org_name)
    org, created = Organization.objects.get_or_create(
        name=org_name,
        defaults={'slug': org_slug, 'description': 'A venture company'}
    )
    if created:
        print(f'Created org: {org.name}')
    else:
        print(f'Found org: {org.name}')

    # 3. Opportunity: Mobile Developer Intern
    opp_title = 'Mobile Developer Intern'
    opp_slug = slugify(f'{org_name} {opp_title}')
    opp, created = Opportunity.objects.get_or_create(
        title=opp_title,
        organization=org,
        defaults={
            'slug': opp_slug,
            'description': 'An exciting internship to work on mobile apps.',
            'opportunity_type': OpportunityType.INTERNSHIP,
            'status': OpportunityStatus.OPEN,
            'created_by': User.objects.filter(is_superuser=True).first() or user,
            'spots_available': 3,
            'is_paid': True
        }
    )
    if created:
        print(f'Created opportunity: {opp.title}')
    else:
        print(f'Found opportunity: {opp.title}')

    # 4. Create Application
    app, created = Application.objects.get_or_create(
        opportunity=opp,
        talent=talent_profile,
        defaults={
            'cover_letter': 'I am very interested in this mobile dev intern role!',
            'status': ApplicationStatus.PENDING
        }
    )
    if created:
        print(f'Created application: Jason Dru for {opp.title}')
    else:
        print(f'Application already exists: Jason Dru for {opp.title}')

if __name__ == '__main__':
    main()

