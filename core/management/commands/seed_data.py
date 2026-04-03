"""
Seed Data Management Command
============================
Creates test users with all roles and seed data for testing.

Usage:
    python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from core.models import CanonicalSkill, CanonicalIndustry
from talents.models import TalentProfile
from organizations.models import Organization, OrganizationMember
from mentors.models import MentorProfile
from schools.models import School, StudentRosterRecord

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with test data for all roles'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding database...\n')
        
        # 1. Create Canonical Skills (with slugs)
        self.stdout.write('Creating skills...')
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
            slug = slugify(name)
            skill, created = CanonicalSkill.objects.get_or_create(
                name=name, 
                defaults={'category': category, 'slug': slug}
            )
            if created:
                self.stdout.write(f'  ✅ Created skill: {name}')
            else:
                self.stdout.write(f'  ⏭️  Skill exists: {name}')
        
        # 2. Create Canonical Industries (with slugs)
        self.stdout.write('\nCreating industries...')
        industries = [
            'Technology', 'Finance', 'Healthcare', 'Education',
            'E-commerce', 'Logistics', 'Agriculture', 'Energy'
        ]
        for name in industries:
            slug = slugify(name)
            industry, created = CanonicalIndustry.objects.get_or_create(
                name=name,
                defaults={'slug': slug}
            )
            if created:
                self.stdout.write(f'  ✅ Created industry: {name}')
            else:
                self.stdout.write(f'  ⏭️  Industry exists: {name}')
        
        # 3. Create Test Users with Different Roles
        self.stdout.write('\nCreating test users...')
        
        # Talent User
        talent_user, created = User.objects.get_or_create(
            email='talent@test.com',
            defaults={
                'username': 'talent_user',
                'full_name': 'Test Talent',
                'is_talent': True,
                'is_org_admin': False,
                'is_mentor': False,
                'is_school_admin': False,
            }
        )
        if created:
            talent_user.set_password('testpass123')
            talent_user.save()
            self.stdout.write('  ✅ Created talent@test.com (is_talent=True)')
        
        # Org Admin User
        org_user, created = User.objects.get_or_create(
            email='orgadmin@test.com',
            defaults={
                'username': 'org_admin_user',
                'full_name': 'Test Org Admin',
                'is_talent': False,
                'is_org_admin': True,
                'is_mentor': False,
                'is_school_admin': False,
            }
        )
        if created:
            org_user.set_password('testpass123')
            org_user.save()
            self.stdout.write('  ✅ Created orgadmin@test.com (is_org_admin=True)')
        
        # Mentor User
        mentor_user, created = User.objects.get_or_create(
            email='mentor@test.com',
            defaults={
                'username': 'mentor_user',
                'full_name': 'Test Mentor',
                'is_talent': False,
                'is_org_admin': False,
                'is_mentor': True,
                'is_school_admin': False,
            }
        )
        if created:
            mentor_user.set_password('testpass123')
            mentor_user.save()
            self.stdout.write('  ✅ Created mentor@test.com (is_mentor=True)')
        
        # School Admin User
        school_user, created = User.objects.get_or_create(
            email='schooladmin@test.com',
            defaults={
                'username': 'school_admin_user',
                'full_name': 'Test School Admin',
                'is_talent': False,
                'is_org_admin': False,
                'is_mentor': False,
                'is_school_admin': True,
            }
        )
        if created:
            school_user.set_password('testpass123')
            school_user.save()
            self.stdout.write('  ✅ Created schooladmin@test.com (is_school_admin=True)')
        
        # Multi-role User (Talent + Mentor)
        multi_user, created = User.objects.get_or_create(
            email='multi@test.com',
            defaults={
                'username': 'multi_role_user',
                'full_name': 'Multi Role User',
                'is_talent': True,
                'is_org_admin': False,
                'is_mentor': True,
                'is_school_admin': False,
            }
        )
        if created:
            multi_user.set_password('testpass123')
            multi_user.save()
            self.stdout.write('  ✅ Created multi@test.com (is_talent=True, is_mentor=True)')
        
        # 4. Create Talent Profile
        self.stdout.write('\nCreating talent profile...')
        talent_profile, created = TalentProfile.objects.get_or_create(
            user=talent_user,
            defaults={
                'headline': 'Full Stack Developer',
                'bio': 'Passionate developer with 3 years experience',
                'education_route': 'university',
                'institution_name': 'University of Lagos',
                'field_of_study': 'Computer Science',
                'graduation_year': 2023,
                'city': 'Lagos',
                'state': 'Lagos State',
                'country': 'Nigeria',
                'is_available': True,
            }
        )
        if created:
            self.stdout.write('  ✅ Created TalentProfile for talent@test.com')
        
        # 5. Create Organization (with slug)
        self.stdout.write('\nCreating organization...')
        tech_industry = CanonicalIndustry.objects.get(name='Technology')
        org, created = Organization.objects.get_or_create(
            name='Acme Tech',
            defaults={
                'slug': 'acme-tech',
                'description': 'Leading tech company in Nigeria',
                'industry': tech_industry,
                'company_size': '51-200',
                'city': 'Lagos',
                'state': 'Lagos State',
                'country': 'Nigeria',
                'website_url': 'https://acmetech.com',
                'is_verified': True,
            }
        )
        if created:
            self.stdout.write('  ✅ Created Organization: Acme Tech')
        else:
            self.stdout.write('  ⏭️  Organization exists: Acme Tech')
        
        # Link org admin to organization
        membership, created = OrganizationMember.objects.get_or_create(
            user=org_user,
            organization=org,
            defaults={'role': 'owner'}
        )
        if created:
            self.stdout.write('  ✅ Linked orgadmin@test.com to Acme Tech')
        else:
            self.stdout.write('  ⏭️  Membership exists')
        
        # 6. Create Mentor Profile
        self.stdout.write('\nCreating mentor profile...')
        mentor_profile, created = MentorProfile.objects.get_or_create(
            user=mentor_user,
            defaults={
                'headline': 'Senior Software Architect',
                'bio': '15+ years experience in building scalable systems',
                'is_accepting_mentees': True,
                'max_mentees': 5,
            }
        )
        if created:
            self.stdout.write('  ✅ Created MentorProfile for mentor@test.com')
        else:
            self.stdout.write('  ⏭️  MentorProfile exists')
        
        # 7. Create School (with slug)
        self.stdout.write('\nCreating school...')
        school, created = School.objects.get_or_create(
            name='University of Lagos',
            defaults={
                'slug': 'university-of-lagos',
                'school_type': 'university',
                'city': 'Lagos',
                'state': 'Lagos State',
                'country': 'Nigeria',
                'website_url': 'https://unilag.edu.ng',
                'is_verified': True,
            }
        )
        if created:
            self.stdout.write('  ✅ Created School: University of Lagos')
        else:
            self.stdout.write('  ⏭️  School exists: University of Lagos')
        
        # Link school admin
        school.admins.add(school_user)
        self.stdout.write('  ✅ Linked schooladmin@test.com to UNILAG')
        
        # 8. Create Sample Student Roster Record
        self.stdout.write('\nCreating student roster record...')
        roster_record, created = StudentRosterRecord.objects.get_or_create(
            school=school,
            matriculation_number='MAT2020001',
            defaults={
                'email': 'student@unilag.edu.ng',
                'full_name': 'Chioma Okafor',
                'department': 'Computer Science',
                'course_of_study': 'BSc Computer Science',
                'enrollment_year': 2020,
                'expected_graduation_year': 2024,
                'is_graduated': False,
                'cgpa': 3.85,
            }
        )
        if created:
            self.stdout.write('  ✅ Created roster record: MAT2020001')
        
        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('✅ Seed data created successfully!'))
        self.stdout.write('='*50)
        self.stdout.write('\n📋 Test Accounts:')
        self.stdout.write('   talent@test.com     - is_talent=True')
        self.stdout.write('   orgadmin@test.com   - is_org_admin=True')
        self.stdout.write('   mentor@test.com     - is_mentor=True')
        self.stdout.write('   schooladmin@test.com - is_school_admin=True')
        self.stdout.write('   multi@test.com      - is_talent=True, is_mentor=True')
        self.stdout.write('\n   Password for all: testpass123')
        self.stdout.write('\n📊 Seed Data:')
        self.stdout.write(f'   Skills: {CanonicalSkill.objects.count()}')
        self.stdout.write(f'   Industries: {CanonicalIndustry.objects.count()}')
        self.stdout.write(f'   Organizations: {Organization.objects.count()}')
        self.stdout.write(f'   Schools: {School.objects.count()}')