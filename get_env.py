"""
Get Supabase Tokens for Test Users
==================================

This script fetches fresh JWT tokens for test users from Supabase Auth.
Use these tokens for Postman API testing.

Usage:
    python get_tokens.py
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

# Common password for all test accounts
COMMON_PASSWORD = "TestPassword123!"

# Test user accounts
TEST_USERS = {
    "Talent": "talent@skillbridge.com",
    "OrgAdmin": "orgadmin@skillbridge.com",
    "Mentor": "mentor@skillbridge.com",
    "SchoolAdmin": "schooladmin@skillbridge.com",
    "Multi": "multi@skillbridge.com"
}


def get_token(email: str, password: str) -> dict:
    """Get JWT token from Supabase for a user."""
    url = f"{SUPABASE_URL}/auth/v1/token?grant_type=password"
    headers = {
        "apikey": SUPABASE_ANON_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(url, headers=headers, json=data, timeout=10)
    
    if response.status_code == 200:
        return {
            "success": True,
            "data": response.json()
        }
    else:
        error_data = response.json()
        return {
            "success": False,
            "error": error_data.get("error_description") or error_data.get("msg") or "Unknown error"
        }


def main():
    """Fetch tokens for all test users."""
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("❌ Error: SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("FETCHING SUPABASE TOKENS FOR TEST USERS")
    print("="*60)
    print(f"Password: {COMMON_PASSWORD}")
    print("="*60 + "\n")
    
    tokens = {}
    
    for role, email in TEST_USERS.items():
        print(f"📧 {role} ({email})")
        
        result = get_token(email, COMMON_PASSWORD)
        
        if result["success"]:
            access_token = result["data"].get("access_token")
            refresh_token = result["data"].get("refresh_token")
            expires_in = result["data"].get("expires_in", 3600)
            
            tokens[role] = {
                "email": email,
                "access_token": access_token,
                "refresh_token": refresh_token
            }
            
            print(f"   ✅ Success! Token expires in {expires_in // 60} minutes")
            print(f"   Token: {access_token[:60]}...\n")
        else:
            print(f"   ❌ Failed: {result['error']}\n")
    
    # Save tokens to file
    if tokens:
        with open("current_tokens.txt", "w") as f:
            f.write("SKILLBRIDGE - CURRENT ACCESS TOKENS\n")
            f.write(f"Generated at: {__import__('datetime').datetime.now()}\n")
            f.write(f"Password: {COMMON_PASSWORD}\n")
            f.write("="*60 + "\n\n")
            
            for role, data in tokens.items():
                f.write(f"[{role}]\n")
                f.write(f"Email: {data['email']}\n")
                f.write(f"Access Token:\n{data['access_token']}\n")
                f.write(f"Refresh Token:\n{data['refresh_token']}\n")
                f.write("-"*60 + "\n\n")
        
        print("✅ Tokens saved to current_tokens.txt")
    
    # Print summary for quick copy-paste
    print("\n" + "="*60)
    print("QUICK COPY - ACCESS TOKENS")
    print("="*60)
    
    for role, data in tokens.items():
        print(f"\n# {role} ({data['email']})")
        print(data['access_token'])


if __name__ == "__main__":
    main()