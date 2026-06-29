"""
Seed Users Management Command
=============================

Creates 10 users per role (talent / mentor / org_admin / school_admin)
with realistic Nigerian-context profile data, plus the dependent rows
each role needs to actually use the app (TalentProfile, MentorProfile,
Organization + OrganizationMember, School + admins membership).

Idempotent: re-running uses get_or_create on email, so it tops up
missing rows without creating duplicates.

Usage:
    python manage.py seed_users
    python manage.py seed_users --reset    # delete previously-seeded
                                           # users (those with the
                                           # @seed.skillbridge.test
                                           # email suffix) first
"""

import random
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from core.models import CanonicalIndustry, CanonicalSkill
from mentors.models import MentorProfile
from organizations.models import Organization, OrganizationMember
from schools.models import School, StudentRosterRecord
from talents.models import TalentProfile, TalentSkill

User = get_user_model()


# Use a sentinel email suffix so --reset can find seeded rows cleanly
# without affecting real users.
SEED_DOMAIN = 'seed.skillbridge.test'
DEFAULT_PASSWORD = 'TestPassword123!'

# Stable seed for reproducibility — re-running produces the same data.
random.seed(42)


# ── Sample data pools ─────────────────────────────────────────────────────────

FIRST_NAMES = [
    'Adaeze', 'Chinedu', 'Tunde', 'Bukola', 'Emeka', 'Funmi', 'Olumide',
    'Ngozi', 'Yusuf', 'Aminat', 'Chiamaka', 'Damilola', 'Ifeoma',
    'Ibrahim', 'Kemi', 'Obinna', 'Oluwaseun', 'Sade', 'Tobechi', 'Zainab',
    'Adekunle', 'Blessing', 'Chigozie', 'Eseosa', 'Folake', 'Halima',
    'Ikenna', 'Joseph', 'Kelechi', 'Lola', 'Maryam', 'Nnamdi', 'Onyeka',
    'Precious', 'Rita', 'Sani', 'Temitope', 'Uchenna', 'Victor', 'Wale',
]

LAST_NAMES = [
    'Okafor', 'Adeyemi', 'Eze', 'Olawale', 'Bello', 'Okoro', 'Ibrahim',
    'Obi', 'Adesina', 'Nwosu', 'Okonkwo', 'Ojo', 'Lawal', 'Akinyemi',
    'Balogun', 'Chukwu', 'Danjuma', 'Edeh', 'Fashola', 'Gbenga',
    'Hassan', 'Igwe', 'Jegede', 'Kalu', 'Lasisi', 'Mohammed',
    'Nnaji', 'Oduya', 'Popoola', 'Rabiu', 'Salami', 'Tijani',
]

CITIES = [
    ('Lagos', 'Lagos State'),
    ('Abuja', 'FCT'),
    ('Ibadan', 'Oyo State'),
    ('Port Harcourt', 'Rivers State'),
    ('Kano', 'Kano State'),
    ('Enugu', 'Enugu State'),
    ('Benin City', 'Edo State'),
    ('Kaduna', 'Kaduna State'),
    ('Jos', 'Plateau State'),
    ('Uyo', 'Akwa Ibom State'),
]

UNIVERSITIES = [
    'University of Lagos', 'University of Ibadan', 'Obafemi Awolowo University',
    'Ahmadu Bello University', 'University of Nigeria, Nsukka',
    'University of Benin', 'Covenant University', 'Babcock University',
    'Lagos State University', 'University of Port Harcourt',
]

FIELDS = [
    'Computer Science', 'Software Engineering', 'Information Systems',
    'Data Science', 'Electrical Engineering', 'Mathematics',
    'Business Administration', 'Statistics', 'Cybersecurity',
    'Information Technology',
]

HEADLINES_TALENT = [
    'Full-stack engineer · React + Django',
    'Backend developer focused on Python and PostgreSQL',
    'Frontend engineer working with React and TypeScript',
    'Mobile developer building with Flutter and Firebase',
    'Data analyst working with SQL, Pandas, and Power BI',
    'DevOps engineer · Docker, Kubernetes, AWS',
    'ML practitioner exploring LLMs and embeddings',
    'Cybersecurity analyst — network defense + pen testing',
    'Cloud engineer building on AWS and Terraform',
    'Product designer transitioning into frontend development',
]

HEADLINES_MENTOR = [
    'Senior Backend Engineer · 10+ years building scalable APIs',
    'Engineering Manager mentoring early-career developers',
    'Staff Frontend Engineer at a Lagos-based fintech',
    'Data Science Lead — kaggle grandmaster, ML educator',
    'CTO turned mentor — startup engineering coach',
    'Cloud Solutions Architect (AWS, GCP)',
    'Director of Engineering, mentoring on architecture and leadership',
    'Mobile Engineering Lead · Android + iOS',
    'Principal Security Engineer — appsec specialist',
    'Engineering Manager · platform & developer experience',
]

ORG_NAMES = [
    ('Acme Tech',          'Technology'),
    ('Paystack Africa',    'Finance'),
    ('Flutterwave Labs',   'Finance'),
    ('Andela Talent',      'Technology'),
    ('Bumpa Commerce',     'E-commerce'),
    ('Eden Health',        'Healthcare'),
    ('Sendbox Logistics',  'Logistics'),
    ('uLesson Learning',   'Education'),
    ('Crop2Cash AgriTech', 'Agriculture'),
    ('Beacon Power',       'Energy'),
]

SCHOOLS = [
    ('University of Lagos',            'university', 'Lagos', 'Lagos State'),
    ('University of Ibadan',           'university', 'Ibadan', 'Oyo State'),
    ('Obafemi Awolowo University',     'university', 'Ile-Ife', 'Osun State'),
    ('Ahmadu Bello University',        'university', 'Zaria', 'Kaduna State'),
    ('University of Nigeria, Nsukka',  'university', 'Nsukka', 'Enugu State'),
    ('Yaba College of Technology',     'polytechnic', 'Lagos', 'Lagos State'),
    ('Federal Polytechnic Auchi',      'polytechnic', 'Auchi', 'Edo State'),
    ('Andela Bootcamp',                'bootcamp',   'Lagos', 'Lagos State'),
    ('Decagon Institute',              'bootcamp',   'Lagos', 'Lagos State'),
    ('AltSchool Africa',               'bootcamp',   'Lagos', 'Lagos State'),
]


def _email(first, last, role):
    """Build a deterministic seeded email for the given role."""
    base = slugify(f'{first}.{last}')
    return f'{base}.{role}@{SEED_DOMAIN}'


def _unique_slug(model, base, field='slug'):
    """Return a slug unique within `model`, adding -2, -3 ... as needed."""
    base_slug = slugify(base)[:200] or 'item'
    candidate = base_slug
    n = 2
    while model.objects.filter(**{field: candidate}).exists():
        candidate = f'{base_slug}-{n}'
        n += 1
    return candidate


class Command(BaseCommand):
    help = 'Seeds 10 users per role (talent, mentor, org_admin, school_admin).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help=f'Delete seeded users ({SEED_DOMAIN}) before re-seeding.',
        )
        parser.add_argument(
            '--per-role', type=int, default=10,
            help='How many users to create per role (default 10).',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        n = options['per_role']

        if options['reset']:
            removed = User.objects.filter(email__iendswith=f'@{SEED_DOMAIN}').delete()[0]
            self.stdout.write(self.style.WARNING(f'Deleted {removed} seeded users.'))

        # Skills must exist for talents to get skill rows. We don't *require*
        # them — seed runs even if seed_data hasn't been run yet — but if they
        # exist we wire them up.
        skill_pool = list(CanonicalSkill.objects.filter(is_active=True))
        industries = {i.name: i for i in CanonicalIndustry.objects.all()}

        created_counts = {
            'talents': 0, 'mentors': 0, 'orgs': 0, 'schools': 0,
        }

        # Talents
        self.stdout.write('\nSeeding talents...')
        for i in range(n):
            first, last = FIRST_NAMES[i % len(FIRST_NAMES)], LAST_NAMES[i % len(LAST_NAMES)]
            email = _email(first, last, 'talent')
            user, was_created = self._get_or_create_user(
                email=email, first=first, last=last, is_talent=True,
            )
            city, state = CITIES[i % len(CITIES)]
            uni = UNIVERSITIES[i % len(UNIVERSITIES)]
            field = FIELDS[i % len(FIELDS)]
            profile, _ = TalentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'headline': HEADLINES_TALENT[i % len(HEADLINES_TALENT)],
                    'bio': f'I am a {field.lower()} graduate based in {city}, '
                           f'looking for impactful opportunities.',
                    'education_route': 'university',
                    'institution_name': uni,
                    'field_of_study': field,
                    'graduation_year': 2020 + (i % 5),
                    'city': city, 'state': state, 'country': 'Nigeria',
                    'is_available': True,
                },
            )
            # Wire up to 3 random skills (only if the canonical list isn't empty)
            if skill_pool:
                chosen = random.sample(skill_pool, k=min(3, len(skill_pool)))
                for s in chosen:
                    TalentSkill.objects.get_or_create(
                        talent=profile, skill=s,
                        defaults={'proficiency': random.choice(
                            ['beginner', 'intermediate', 'advanced'],
                        ), 'years_experience': random.randint(0, 4)},
                    )
            if was_created:
                created_counts['talents'] += 1
                self.stdout.write(f'  + {email}')

        # Mentors
        self.stdout.write('\nSeeding mentors...')
        for i in range(n):
            # Offset names so mentors don't collide with talents on (first,last).
            first = FIRST_NAMES[(i + 10) % len(FIRST_NAMES)]
            last  = LAST_NAMES[(i + 5)  % len(LAST_NAMES)]
            email = _email(first, last, 'mentor')
            user, was_created = self._get_or_create_user(
                email=email, first=first, last=last, is_mentor=True,
            )
            MentorProfile.objects.get_or_create(
                user=user,
                defaults={
                    'headline': HEADLINES_MENTOR[i % len(HEADLINES_MENTOR)],
                    'bio': 'Open to mentoring focused, motivated talents. '
                           'I prefer weekly sessions and clear learning goals.',
                    'is_accepting_mentees': True,
                    'max_mentees': random.choice([3, 5, 8]),
                    'is_verified': True,
                },
            )
            if was_created:
                created_counts['mentors'] += 1
                self.stdout.write(f'  + {email}')

        # Organizations + Org Admins
        self.stdout.write('\nSeeding organizations + org admins...')
        for i in range(n):
            org_name, industry_name = ORG_NAMES[i % len(ORG_NAMES)]
            # If we need more than 10 orgs (per-role > 10), suffix with index.
            display_name = org_name if i < len(ORG_NAMES) else f'{org_name} {i}'

            first = FIRST_NAMES[(i + 3)  % len(FIRST_NAMES)]
            last  = LAST_NAMES[(i + 12) % len(LAST_NAMES)]
            email = _email(first, last, 'org')
            user, was_created = self._get_or_create_user(
                email=email, first=first, last=last, is_org_admin=True,
            )

            # Try to find an existing org by name (idempotent), else create.
            org = Organization.objects.filter(name=display_name).first()
            if org is None:
                org = Organization.objects.create(
                    name=display_name,
                    slug=_unique_slug(Organization, display_name),
                    description=f'{display_name} hires and trains talent across Nigeria.',
                    industry=industries.get(industry_name),
                    company_size=random.choice(['11-50', '51-200', '201-500']),
                    city=CITIES[i % len(CITIES)][0],
                    state=CITIES[i % len(CITIES)][1],
                    country='Nigeria',
                    website_url=f'https://{slugify(display_name)}.com',
                    is_verified=True,
                )
                self.stdout.write(f'  + org "{display_name}"')

            OrganizationMember.objects.get_or_create(
                organization=org, user=user,
                defaults={'role': OrganizationMember.MemberRole.OWNER},
            )
            if was_created:
                created_counts['orgs'] += 1
                self.stdout.write(f'  + {email} -> owner of {display_name}')

        # Schools + School Admins
        self.stdout.write('\nSeeding schools + school admins...')
        for i in range(n):
            school_name, stype, city, state = SCHOOLS[i % len(SCHOOLS)]
            display = school_name if i < len(SCHOOLS) else f'{school_name} ({i})'

            first = FIRST_NAMES[(i + 7)  % len(FIRST_NAMES)]
            last  = LAST_NAMES[(i + 20) % len(LAST_NAMES)]
            email = _email(first, last, 'school')
            user, was_created = self._get_or_create_user(
                email=email, first=first, last=last, is_school_admin=True,
            )

            school = School.objects.filter(name=display).first()
            if school is None:
                school = School.objects.create(
                    name=display,
                    slug=_unique_slug(School, display),
                    school_type=stype,
                    city=city, state=state, country='Nigeria',
                    website_url=f'https://{slugify(display)}.edu.ng',
                    contact_email=f'registrar@{slugify(display)}.edu.ng',
                    is_verified=True,
                )
                # Seed a couple of roster records so the dashboard has something
                # to show without a separate command.
                for r in range(3):
                    StudentRosterRecord.objects.get_or_create(
                        school=school,
                        matriculation_number=f'{slugify(display)[:10].upper()}{i}{r:03d}',
                        defaults={
                            'full_name': f'{FIRST_NAMES[(i + r) % len(FIRST_NAMES)]} '
                                         f'{LAST_NAMES[(i + r) % len(LAST_NAMES)]}',
                            'email': f'student{i}{r}@{slugify(display)}.edu.ng',
                            'department': FIELDS[(i + r) % len(FIELDS)],
                            'course_of_study': FIELDS[(i + r) % len(FIELDS)],
                            'enrollment_year': 2020 + (r % 3),
                            'expected_graduation_year': 2024 + (r % 3),
                            'cgpa': round(2.5 + random.random() * 1.5, 2),
                        },
                    )
                self.stdout.write(f'  + school "{display}"')

            school.admins.add(user)
            if was_created:
                created_counts['schools'] += 1
                self.stdout.write(f'  + {email} -> admin of {display}')

        # Summary
        self.stdout.write(self.style.SUCCESS('\nDone.'))
        self.stdout.write('Created (new this run):')
        for k, v in created_counts.items():
            self.stdout.write(f'  {k:>10}: {v}')
        self.stdout.write('\nLogin with any of the seeded emails using password:')
        self.stdout.write(f'    {DEFAULT_PASSWORD}')
        self.stdout.write(f'\nList seeded users:')
        self.stdout.write(
            f'    User.objects.filter(email__iendswith="@{SEED_DOMAIN}")'
        )

    # helpers

    def _get_or_create_user(self, *, email, first, last, **role_flags):
        """get_or_create a user, setting the role flag and email_verified."""
        existing = User.objects.filter(email__iexact=email).first()
        if existing is not None:
            changed = False
            for flag, val in role_flags.items():
                if getattr(existing, flag) != val:
                    setattr(existing, flag, val)
                    changed = True
            if not existing.email_verified:
                existing.email_verified = True
                changed = True
            if changed:
                existing.save()
            return existing, False

        user = User.objects.create_user(
            username=email,
            email=email,
            password=DEFAULT_PASSWORD,
            full_name=f'{first} {last}',
            phone_number=f'+234{random.randint(7000000000, 9099999999)}',
        )
        for flag, val in role_flags.items():
            setattr(user, flag, val)
        user.email_verified = True  # skip verification step for seeded accounts
        user.save()
        return user, True
