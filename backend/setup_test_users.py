"""
Clean User Setup Script for SkillBridge
========================================

This script:
1. Deletes all existing test users from Django
2. Creates new test users via Supabase Auth API (proper flow)
3. Creates associated profiles (TalentProfile, MentorProfile, etc.)
4. Outputs credentials and tokens for Postman testing

Usage:
    python manage.py shell < setup_test_users.py
    
    OR
    
    python setup_test_users.py

Password for all test accounts: TestPassword123!
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Add project to path if running standalone
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

django.setup()

# Now we can import Django models
from django.db import transaction
from users.models import User
from users.services import SupabaseAuthService, SupabaseAuthError
from talents.models import TalentProfile
from mentors.models import MentorProfile
from organizations.models import Organization, OrganizationMember
from schools.models import School


# =============================================================================
# CONFIGURATION
# =============================================================================

TEST_PASSWORD = "TestPassword123!"

TEST_USERS = [
    {
        "email": "talent@skillbridge.com",
        "full_name": "Test Talent",
        "role": "talent",
        "phone_number": "+2348012345671"
    },
    {
        "email": "orgadmin@skillbridge.com", 
        "full_name": "Test Org Admin",
        "role": "org_admin",
        "phone_number": "+2348012345672"
    },
    {
        "email": "mentor@skillbridge.com",
        "full_name": "Test Mentor",
        "role": "mentor",
        "phone_number": "+2348012345673"
    },
    {
        "email": "schooladmin@skillbridge.com",
        "full_name": "Test School Admin",
        "role": "school_admin",
        "phone_number": "+2348012345674"
    },
    {
        "email": "multi@skillbridge.com",
        "full_name": "Multi Role User",
        "role": "talent",  # Will add mentor role after creation
        "phone_number": "+2348012345675"
    }
]


def delete_existing_users():
    """Delete all test users from Django."""
    print("\n" + "="*60)
    print("STEP 1: DELETING EXISTING TEST USERS")
    print("="*60)
    
    test_emails = [u["email"] for u in TEST_USERS]
    
    # Delete from Django
    deleted_count = User.objects.filter(email__in=test_emails).delete()[0]
    print(f"✅ Deleted {deleted_count} users from Django")
    
    # Note: Cannot delete from Supabase without service key
    # Users will be recreated if they exist
    print("ℹ️  Note: Existing Supabase users will error on signup (that's OK)")


def create_test_organization():
    """Create test organization if it doesn't exist."""
    org, created = Organization.objects.get_or_create(
        slug='acme-tech',
        defaults={
            'name': 'Acme Tech Solutions',
            'description': 'A leading tech company in Nigeria',
            'website_url': 'https://acmetech.com.ng',
            'city': 'Lagos',
            'state': 'Lagos',
            'country': 'Nigeria',
            'company_size': '11-50',
            'is_verified': True
        }
    )
    status = "Created" if created else "Already exists"
    print(f"✅ Organization: {org.name} ({status})")
    return org


def create_test_school():
    """Create test school if it doesn't exist."""
    school, created = School.objects.get_or_create(
        slug='unilag',
        defaults={
            'name': 'University of Lagos',
            'website_url': 'https://unilag.edu.ng',
            'city': 'Akoka',
            'state': 'Lagos',
            'country': 'Nigeria',
            'school_type': 'university',
            'is_verified': True
        }
    )
    status = "Created" if created else "Already exists"
    print(f"✅ School: {school.name} ({status})")
    return school


def create_user_via_supabase(user_data: dict, auth_service: SupabaseAuthService) -> tuple:
    """
    Create a single user via Supabase Auth API.
    
    Returns: (django_user, tokens) or (None, error_message)
    """
    try:
        user, tokens = auth_service.sign_up(
            email=user_data["email"],
            password=TEST_PASSWORD,
            full_name=user_data["full_name"],
            role=user_data["role"],
            phone_number=user_data.get("phone_number", ""),
            auto_confirm=True
        )
        return user, tokens
        
    except SupabaseAuthError as e:
        # If user already exists in Supabase, try to sign in instead
        if "already" in e.message.lower() or e.error_code == "user_already_exists":
            try:
                user, tokens = auth_service.sign_in(
                    email=user_data["email"],
                    password=TEST_PASSWORD
                )
                # Update role flags for existing user
                update_role_flags(user, user_data["role"])
                return user, tokens
            except SupabaseAuthError as login_error:
                return None, f"Signup failed, login also failed: {login_error.message}"
        
        return None, e.message


def update_role_flags(user: User, role: str):
    """Update user role flags based on role string."""
    if role == 'talent':
        user.is_talent = True
    elif role == 'org_admin':
        user.is_org_admin = True
    elif role == 'mentor':
        user.is_mentor = True
    elif role == 'school_admin':
        user.is_school_admin = True
    user.save()


def create_talent_profile(user: User):
    """Create TalentProfile for a talent user."""
    profile, created = TalentProfile.objects.get_or_create(
        user=user,
        defaults={
            'headline': 'Full Stack Developer | Python & React',
            'bio': 'Passionate developer looking for opportunities to grow.',
            'education_route': 'university',
            'is_available': True,
            'city': 'Lagos',
            'state': 'Lagos',
            'country': 'Nigeria'
        }
    )
    return profile, created


def create_mentor_profile(user: User):
    """Create MentorProfile for a mentor user."""
    profile, created = MentorProfile.objects.get_or_create(
        user=user,
        defaults={
            'headline': 'Senior Software Architect | Tech Mentor',
            'bio': '15+ years of experience in software development.',
            'is_accepting_mentees': True,
            'max_mentees': 5
        }
    )
    return profile, created


def create_org_membership(user: User, org: Organization):
    """Create OrganizationMember for an org admin user."""
    membership, created = OrganizationMember.objects.get_or_create(
        user=user,
        organization=org,
        defaults={
            'role': 'admin'
        }
    )
    return membership, created


def link_school_admin(user: User, school: School):
    """Link school admin user to a school."""
    # Add user to school's admins M2M
    school.admins.add(user)
    user.is_school_admin = True
    user.save()
    print(f"   ✅ Linked as admin of {school.name}")


def main():
    """Main execution function."""
    print("\n" + "="*60)
    print("SKILLBRIDGE TEST USER SETUP")
    print("="*60)
    print(f"Password for all accounts: {TEST_PASSWORD}")
    print("="*60)
    
    # Step 1: Delete existing users
    delete_existing_users()
    
    # Step 2: Create supporting data
    print("\n" + "="*60)
    print("STEP 2: CREATING SUPPORTING DATA")
    print("="*60)
    
    org = create_test_organization()
    school = create_test_school()
    
    # Step 3: Create users via Supabase
    print("\n" + "="*60)
    print("STEP 3: CREATING USERS VIA SUPABASE AUTH")
    print("="*60)
    
    try:
        auth_service = SupabaseAuthService()
    except SupabaseAuthError as e:
        print(f"❌ Failed to initialize auth service: {e.message}")
        print("   Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in .env")
        sys.exit(1)
    
    created_users = []
    
    for user_data in TEST_USERS:
        print(f"\n📧 Creating: {user_data['email']}")
        
        user, result = create_user_via_supabase(user_data, auth_service)
        
        if user is None:
            print(f"   ❌ Failed: {result}")
            continue
        
        tokens = result
        print(f"   ✅ Django User ID: {user.id}")
        print(f"   ✅ Supabase UID: {user.supabase_uid}")
        
        # Create role-specific profiles
        role = user_data["role"]
        
        if role == 'talent' or user_data["email"] == "multi@skillbridge.com":
            profile, _ = create_talent_profile(user)
            print(f"   ✅ TalentProfile created")
        
        if role == 'org_admin':
            membership, _ = create_org_membership(user, org)
            print(f"   ✅ OrganizationMember created for {org.name}")
        
        if role == 'mentor' or user_data["email"] == "multi@skillbridge.com":
            profile, _ = create_mentor_profile(user)
            if user_data["email"] == "multi@skillbridge.com":
                user.is_mentor = True
                user.save()
            print(f"   ✅ MentorProfile created")
        
        if role == 'school_admin':
            link_school_admin(user, school)
        
        created_users.append({
            "email": user_data["email"],
            "password": TEST_PASSWORD,
            "role": role,
            "access_token": tokens.get("access_token"),
            "refresh_token": tokens.get("refresh_token"),
            "django_id": user.id,
            "supabase_uid": user.supabase_uid
        })
    
    # Step 4: Output summary
    print("\n" + "="*60)
    print("STEP 4: SUMMARY - TEST CREDENTIALS")
    print("="*60)
    
    print(f"\n{'Email':<30} {'Role':<15} {'Status'}")
    print("-"*60)
    
    for u in created_users:
        print(f"{u['email']:<30} {u['role']:<15} ✅ Ready")
    
    print(f"\n🔑 Password for all accounts: {TEST_PASSWORD}")
    
    # Output tokens for Postman
    print("\n" + "="*60)
    print("ACCESS TOKENS FOR POSTMAN (valid for ~1 hour)")
    print("="*60)
    
    for u in created_users:
        if u.get("access_token"):
            print(f"\n📧 {u['email']} ({u['role']}):")
            print(f"   Token: {u['access_token'][:50]}...")
    
    # Save tokens to a file for easy access
    with open("test_tokens.txt", "w") as f:
        f.write("SKILLBRIDGE TEST TOKENS\n")
        f.write(f"Password for all: {TEST_PASSWORD}\n")
        f.write("="*60 + "\n\n")
        
        for u in created_users:
            f.write(f"Email: {u['email']}\n")
            f.write(f"Role: {u['role']}\n")
            f.write(f"Django ID: {u['django_id']}\n")
            f.write(f"Supabase UID: {u['supabase_uid']}\n")
            f.write(f"Access Token: {u.get('access_token', 'N/A')}\n")
            f.write(f"Refresh Token: {u.get('refresh_token', 'N/A')}\n")
            f.write("-"*60 + "\n")
    
    print("\n✅ Tokens saved to test_tokens.txt")
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)


if __name__ == "__main__":
    main()
