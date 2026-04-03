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
from django.utils import timezone
from datetime import timedelta
from core.models import CanonicalSkill, CanonicalIndustry
from talents.models import TalentProfile, TalentSkill
from organizations.models import Organization, OrganizationMember
from mentors.models import MentorProfile
from schools.models import School, StudentRosterRecord
from opportunities.models import Opportunity, Application

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
        skills = {}
        for name, category in skills_data:
            slug = slugify(name)
            skill, created = CanonicalSkill.objects.get_or_create(
                name=name, 
                defaults={'category': category, 'slug': slug}
            )
            skills[name] = skill
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
        industries_dict = {}
        for name in industries:
            slug = slugify(name)
            industry, created = CanonicalIndustry.objects.get_or_create(
                name=name,
                defaults={'slug': slug}
            )
            industries_dict[name] = industry
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
        
        # Create TalentProfile for multi-role user too
        multi_talent_profile, created = TalentProfile.objects.get_or_create(
            user=multi_user,
            defaults={
                'headline': 'Developer & Mentor',
                'bio': 'Experienced developer who also mentors',
                'education_route': 'bootcamp',
                'institution_name': 'Andela Bootcamp',
                'field_of_study': 'Software Engineering',
                'graduation_year': 2021,
                'city': 'Abuja',
                'state': 'FCT',
                'country': 'Nigeria',
                'is_available': True,
            }
        )
        if created:
            self.stdout.write('  ✅ Created TalentProfile for multi@test.com')
        
        # 4b. Add Skills to Talent Profiles
        self.stdout.write('\nAdding skills to talent profiles...')
        talent_skills_data = [
            (talent_profile, 'Python', 'advanced', 3, True),
            (talent_profile, 'Django', 'advanced', 2, True),
            (talent_profile, 'JavaScript', 'intermediate', 2, False),
            (talent_profile, 'React', 'intermediate', 1, False),
            (multi_talent_profile, 'Python', 'expert', 5, True),
            (multi_talent_profile, 'AWS', 'advanced', 3, True),
        ]
        for profile, skill_name, proficiency, years, is_primary in talent_skills_data:
            ts, created = TalentSkill.objects.get_or_create(
                talent=profile,
                skill=skills[skill_name],
                defaults={
                    'proficiency': proficiency,
                    'years_experience': years,
                    'is_primary': is_primary,
                }
            )
            if created:
                self.stdout.write(f'  ✅ Added {skill_name} to {profile.user.email}')
        
        # 5. Create Organization (with slug)
        self.stdout.write('\nCreating organization...')
        tech_industry = industries_dict['Technology']
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
        
        # Create MentorProfile for multi-role user
        multi_mentor_profile, created = MentorProfile.objects.get_or_create(
            user=multi_user,
            defaults={
                'headline': 'Full Stack Mentor',
                'bio': 'Helping developers grow their careers',
                'is_accepting_mentees': True,
                'max_mentees': 3,
            }
        )
        if created:
            self.stdout.write('  ✅ Created MentorProfile for multi@test.com')
        
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
        
        # =====================================================================
        # 9. CREATE OPPORTUNITIES (Critical for 403/404 testing)
        # =====================================================================
        self.stdout.write('\nCreating opportunities...')
        
        # Opportunity created by Organization
        opp_org, created = Opportunity.objects.get_or_create(
            slug='backend-internship-acme',
            defaults={
                'title': 'Backend Developer Internship',
                'description': 'Join our backend team to build scalable APIs using Django and PostgreSQL.',
                'organization': org,
                'created_by': org_user,
                'opportunity_type': 'internship',
                'location': 'Lagos, Nigeria',
                'is_remote': False,
                'experience_level': 'entry',
                'duration': '3 months',
                'is_paid': True,
                'compensation': '₦150,000/month',
                'application_deadline': timezone.now() + timedelta(days=30),
                'start_date': timezone.now() + timedelta(days=45),
                'spots_available': 3,
                'status': 'published',
                'published_at': timezone.now(),
            }
        )
        if created:
            opp_org.required_skills.add(skills['Python'], skills['Django'], skills['PostgreSQL'])
            self.stdout.write('  ✅ Created Opportunity: Backend Developer Internship (by Org)')
        
        # Another opportunity by same org (for list testing)
        opp_org2, created = Opportunity.objects.get_or_create(
            slug='frontend-internship-acme',
            defaults={
                'title': 'Frontend Developer Internship',
                'description': 'Build beautiful UIs with React and TypeScript.',
                'organization': org,
                'created_by': org_user,
                'opportunity_type': 'internship',
                'location': 'Lagos, Nigeria',
                'is_remote': True,
                'experience_level': 'entry',
                'duration': '3 months',
                'is_paid': True,
                'compensation': '₦120,000/month',
                'application_deadline': timezone.now() + timedelta(days=45),
                'start_date': timezone.now() + timedelta(days=60),
                'spots_available': 2,
                'status': 'published',
                'published_at': timezone.now(),
            }
        )
        if created:
            opp_org2.required_skills.add(skills['JavaScript'], skills['React'], skills['TypeScript'])
            self.stdout.write('  ✅ Created Opportunity: Frontend Developer Internship (by Org)')
        
        # Opportunity created by Mentor (Guided Project)
        opp_mentor, created = Opportunity.objects.get_or_create(
            slug='ml-guided-project',
            defaults={
                'title': 'Machine Learning Guided Project',
                'description': 'Learn ML fundamentals by building a real recommendation system.',
                'mentor': mentor_profile,
                'created_by': mentor_user,
                'opportunity_type': 'guided_project',
                'location': 'Remote',
                'is_remote': True,
                'experience_level': 'intermediate',
                'duration': '6 weeks',
                'is_paid': False,
                'application_deadline': timezone.now() + timedelta(days=14),
                'start_date': timezone.now() + timedelta(days=21),
                'spots_available': 5,
                'max_applicants': 20,
                'status': 'published',
                'published_at': timezone.now(),
            }
        )
        if created:
            opp_mentor.required_skills.add(skills['Python'], skills['Machine Learning'])
            self.stdout.write('  ✅ Created Opportunity: ML Guided Project (by Mentor)')
        
        # Draft opportunity (for testing draft vs published)
        opp_draft, created = Opportunity.objects.get_or_create(
            slug='devops-internship-draft',
            defaults={
                'title': 'DevOps Engineer Internship (DRAFT)',
                'description': 'Learn AWS and Docker in a production environment.',
                'organization': org,
                'created_by': org_user,
                'opportunity_type': 'internship',
                'location': 'Lagos, Nigeria',
                'is_remote': True,
                'experience_level': 'entry',
                'duration': '6 months',
                'is_paid': True,
                'compensation': '₦200,000/month',
                'application_deadline': timezone.now() + timedelta(days=60),
                'start_date': timezone.now() + timedelta(days=90),
                'spots_available': 1,
                'status': 'draft',  # Not published yet
            }
        )
        if created:
            opp_draft.required_skills.add(skills['AWS'], skills['Docker'])
            self.stdout.write('  ✅ Created Opportunity: DevOps Internship (DRAFT)')
        
        # =====================================================================
        # 10. CREATE APPLICATIONS (Critical for 403/404 testing)
        # =====================================================================
        self.stdout.write('\nCreating applications...')
        
        # Talent applies to org opportunity
        app1, created = Application.objects.get_or_create(
            opportunity=opp_org,
            talent=talent_profile,
            defaults={
                'cover_letter': 'I am very interested in this backend position. I have experience with Python and Django.',
                'status': 'pending',
            }
        )
        if created:
            self.stdout.write('  ✅ Created Application: talent@test.com -> Backend Internship')
        
        # Talent applies to mentor's guided project
        app2, created = Application.objects.get_or_create(
            opportunity=opp_mentor,
            talent=talent_profile,
            defaults={
                'cover_letter': 'I want to learn ML from an experienced mentor.',
                'status': 'pending',
            }
        )
        if created:
            self.stdout.write('  ✅ Created Application: talent@test.com -> ML Guided Project')
        
        # Multi-role user also applies (to test multiple applications)
        app3, created = Application.objects.get_or_create(
            opportunity=opp_org,
            talent=multi_talent_profile,
            defaults={
                'cover_letter': 'Applying as a multi-role user with mentor experience.',
                'status': 'reviewing',  # Different status for testing
            }
        )
        if created:
            self.stdout.write('  ✅ Created Application: multi@test.com -> Backend Internship')
        
        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('✅ Seed data created successfully!'))
        self.stdout.write('='*60)
        self.stdout.write('\n📋 Test Accounts:')
        self.stdout.write('   talent@test.com      - is_talent=True')
        self.stdout.write('   orgadmin@test.com    - is_org_admin=True + owns Acme Tech')
        self.stdout.write('   mentor@test.com      - is_mentor=True + owns ML Project')
        self.stdout.write('   schooladmin@test.com - is_school_admin=True + admin of UNILAG')
        self.stdout.write('   multi@test.com       - is_talent=True, is_mentor=True')
        self.stdout.write('\n   Password for all: testpass123')
        self.stdout.write('\n📊 Seed Data Created:')
        self.stdout.write(f'   Skills: {CanonicalSkill.objects.count()}')
        self.stdout.write(f'   Industries: {CanonicalIndustry.objects.count()}')
        self.stdout.write(f'   Organizations: {Organization.objects.count()}')
        self.stdout.write(f'   Schools: {School.objects.count()}')
        self.stdout.write(f'   Opportunities: {Opportunity.objects.count()}')
        self.stdout.write(f'   Applications: {Application.objects.count()}')
        self.stdout.write(f'   Talent Skills: {TalentSkill.objects.count()}')
        
        self.stdout.write('\n🔐 Ownership for 403/404 Testing:')
        self.stdout.write('   orgadmin@test.com owns:')
        self.stdout.write('     - Acme Tech organization')
        self.stdout.write('     - Backend Internship, Frontend Internship, DevOps Draft')
        self.stdout.write('   mentor@test.com owns:')
        self.stdout.write('     - ML Guided Project')
        self.stdout.write('   talent@test.com owns:')
        self.stdout.write('     - 2 applications (Backend Internship, ML Project)')
        self.stdout.write('   multi@test.com owns:')
        self.stdout.write('     - 1 application (Backend Internship)')
        self.stdout.write('='*60)