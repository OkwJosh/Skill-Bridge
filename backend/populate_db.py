
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from talents.models import TalentProfile
from organizations.models import Organization, OrganizationMember
from opportunities.models import Opportunity, Application, OpportunityType, OpportunityStatus, ApplicationStatus
from core.models import Category, CanonicalSkill
from django.utils.text import slugify

User = get_user_model()

def main():
    print('Creating dummy data...')
    
    # Categories & Skills
    cat, _ = Category.objects.get_or_create(name='Engineering', slug='engineering')
    skill, _ = CanonicalSkill.objects.get_or_create(name='Flutter', slug='flutter')

    # 1. Organization Admin
    org_admin, _ = User.objects.get_or_create(
        email='org@example.com',
        defaults={'username': 'org@example.com', 'full_name': 'Sarah Connors', 'is_org_admin': True, 'email_verified': True}
    )
    org_admin.set_password('password123')
    org_admin.save()
    
    org_name = 'Tech Innovators Inc'
    org, _ = Organization.objects.get_or_create(
        name=org_name,
        defaults={'slug': slugify(org_name), 'description': 'Leading tech company.', 'city': 'San Francisco'}
    )
    OrganizationMember.objects.get_or_create(organization=org, user=org_admin, role='admin')

    # 2. Talent
    talent_user, _ = User.objects.get_or_create(
        email='talent@example.com',
        defaults={'username': 'talent@example.com', 'full_name': 'John Doe', 'is_talent': True, 'email_verified': True}
    )
    talent_user.set_password('password123')
    talent_user.save()
    
    talent_profile, _ = TalentProfile.objects.get_or_create(
        user=talent_user,
        defaults={'headline': 'Mobile Developer (Flutter)', 'bio': 'Passionate about apps.'}
    )

    # 3. Opportunity
    opp_title = 'Flutter Developer Intern'
    opp, _ = Opportunity.objects.get_or_create(
        title=opp_title,
        organization=org,
        defaults={
            'slug': slugify(f'{org_name} {opp_title}'),
            'description': 'We are looking for a Flutter intern.',
            'opportunity_type': OpportunityType.INTERNSHIP,
            'status': OpportunityStatus.OPEN,
            'created_by': org_admin,
            'category': cat,
            'is_remote': True
        }
    )
    opp.required_skills.add(skill)

    # 4. Application
    app, _ = Application.objects.get_or_create(
        opportunity=opp,
        talent=talent_profile,
        defaults={
            'cover_letter': 'I am the perfect fit for this role!',
            'status': ApplicationStatus.PENDING
        }
    )
    
    print('Done!')
    print('Organization Login -> Email: org@example.com | Password: password123')
    print('Talent Login -> Email: talent@example.com | Password: password123')

if __name__ == '__main__':
    main()

