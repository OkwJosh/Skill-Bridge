#!/usr/bin/env python
"""
SkillBridge — JWT Token Generator
Run with: python generate_tokens.py
Make sure this file is in the same directory as manage.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')  # change 'config' to your actual settings module name
django.setup()

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

emails = [
    'talent@skillbridge.com',
    'orgadmin@skillbridge.com',
    'mentor@skillbridge.com',
    'schooladmin@skillbridge.com',
    'multi@skillbridge.com',
]

print("\n" + "="*80)
print("  SKILLBRIDGE — JWT TOKEN GENERATOR")
print("="*80)

for email in emails:
    try:
        user = User.objects.get(email=email)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        print(f"\n EMAIL   : {email}")
        print(f" ROLE    : {getattr(user, 'role', 'N/A')}")
        print(f" ACCESS  : {access_token}")
        print(f" REFRESH : {refresh_token}")
        print("-"*80)

    except User.DoesNotExist:
        print(f"\n  {email} — user not found in database")
        print("-"*80)

print("\n Done. Paste ACCESS token into Postman as Bearer Token.\n")