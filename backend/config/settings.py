"""
SkillBridge Django Settings
===========================
Multi-Sided Opportunity Marketplace Backend

Database: Supabase PostgreSQL
Storage: Supabase Storage (S3-compatible)
Authentication: Supabase Auth (JWT verification)
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load environment variables from .env file (for local development)
load_dotenv()

# =============================================================================
# BASE CONFIGURATION
# =============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: Move to environment variable in production!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'django-insecure-change-me-in-production')

# SECURITY: Set to False in production
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')


# =============================================================================
# APPLICATION DEFINITION
# =============================================================================

INSTALLED_APPS = [
    # Django built-in apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party apps
    'rest_framework',           # Django REST Framework
    'rest_framework_simplejwt',  # JWT authentication support
    'corsheaders',              # CORS handling
    'django_filters',           # DRF filtering
    'drf_spectacular',          # OpenAPI documentation
    'storages',                 # S3-compatible storage (Supabase)
    
    # Local apps - SkillBridge modules
    'users',                    # Custom User model & authentication
    'core',                     # Taxonomy (Skills, Industries) & shared utilities
    'talents',                  # Talent profiles
    'organizations',            # Organization profiles
    'opportunities',            # Internships & micro-projects
    'mentors',                  # Mentor profiles & guided projects
    'schools',                  # School admin (Data Trust)
    'ai_engine',                # AI matching / trust engine
    'notifications',            # In-app notification feed (signal-driven)
]

MIDDLEWARE = [
    # CORS must be as high as possible, especially before CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    # WhiteNoise for static files in production
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# =============================================================================
# DATABASE - SUPABASE POSTGRESQL
# =============================================================================
# Connection string format from Supabase Dashboard > Settings > Database:
# postgres://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
#
# Set this in your .env file as SUPABASE_DB_URL

SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')

if SUPABASE_DB_URL:
    # Production: Use Supabase PostgreSQL
    DATABASES = {
        'default': dj_database_url.config(
            default=SUPABASE_DB_URL,
            conn_max_age=0,  # CRITICAL: Must be 0 when using Supabase pooler to prevent EMAXCONNSESSION limits
            conn_health_checks=True,  # Verify connection health before use
        )
    }
else:
    # Development fallback: SQLite for local testing without Supabase
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# =============================================================================
# CUSTOM USER MODEL
# =============================================================================
# CRITICAL: Must be set BEFORE running migrations for the first time!

AUTH_USER_MODEL = 'users.User'


# =============================================================================
# SIMPLE JWT CONFIGURATION
# =============================================================================
# Django REST Framework Simple JWT for authentication.
# Tokens are generated by Django and issued to users on login.

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),  # 1 hour
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),     # 7 days
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,  # Use Django SECRET_KEY
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'users.authentication.user_authentication_rule',
    'JTI_CLAIM': 'jti',
}


# =============================================================================
# EMAIL (password reset, etc.)
# =============================================================================
# Dev default: print emails to the runserver console.
# Prod: set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend and
# the EMAIL_HOST / EMAIL_HOST_USER / EMAIL_HOST_PASSWORD / EMAIL_PORT /
# EMAIL_USE_TLS env vars.
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.console.EmailBackend',
)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'no-reply@skillbridge.local')

# Frontend origin used to build links in outgoing emails (password reset, etc.)
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')


# =============================================================================
# OAUTH (Sign in with Google / Apple)
# =============================================================================
# When these are unset, the corresponding sign-in endpoint returns
# 503 oauth_disabled and the frontend hides the button. Same pattern as
# AI Engine's ai_disabled mode.
#
# Google: from Google Cloud Console → Credentials → OAuth 2.0 Client ID (web)
# Apple : Service ID (e.g. `com.skillbridge.web`) from Apple Developer Console
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
APPLE_SERVICE_ID = os.getenv('APPLE_SERVICE_ID', '')


# =============================================================================
# AI ENGINE
# =============================================================================
# Hard cap (seconds) on a single Gemini call from MatchCVView. Tune based on
# observed p99 latency; the worker thread is abandoned (not killed) on
# timeout, so keep this tight.
AI_CALL_TIMEOUT_SECONDS = int(os.getenv('AI_CALL_TIMEOUT_SECONDS', '30'))


# =============================================================================
# SUPABASE STORAGE - S3-COMPATIBLE CONFIGURATION
# =============================================================================
# Supabase Storage provides an S3-compatible API for file uploads.
# Used for: profile photos, resumes, project attachments, etc.
#
# Get these credentials from: Supabase Dashboard > Settings > API
# Or create S3 credentials at: Storage > S3 Access Keys

# Enable Supabase Storage only if credentials are provided
USE_SUPABASE_STORAGE = os.getenv('AWS_ACCESS_KEY_ID') is not None

if USE_SUPABASE_STORAGE:
    # File storage backend
    STORAGES = {
        'default': {
            'BACKEND': 'storages.backends.s3boto3.S3Boto3Storage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
        },
    }
    
    # Supabase S3-compatible credentials
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'skillbridge')
    
    # CRITICAL: Supabase S3 endpoint URL format
    # Format: https://<project-ref>.supabase.co/storage/v1/s3
    AWS_S3_ENDPOINT_URL = os.getenv('AWS_S3_ENDPOINT_URL')
    
    # S3 settings for Supabase compatibility
    AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'auto')
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_DEFAULT_ACL = None  # Supabase handles ACLs differently
    AWS_QUERYSTRING_AUTH = True  # Generate signed URLs
    AWS_S3_FILE_OVERWRITE = False  # Don't overwrite files with same name


# =============================================================================
# DJANGO REST FRAMEWORK CONFIGURATION
# =============================================================================

REST_FRAMEWORK = {
    # Authentication: Use Simple JWT
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    
    # Default permission: Require authentication
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    
    # Custom exception handler for standard JSON envelope
    'EXCEPTION_HANDLER': 'core.exceptions.standard_exception_handler',
    
    # Custom renderer for standard JSON envelope
    'DEFAULT_RENDERER_CLASSES': [
        'core.renderers.StandardJSONRenderer',
    ],
    
    # Filtering
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    
    # OpenAPI schema
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}


# =============================================================================
# CORS CONFIGURATION
# =============================================================================
# Configure which frontend origins can access the API

CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')

CORS_ALLOW_CREDENTIALS = True  # Allow cookies/auth headers


# =============================================================================
# API DOCUMENTATION (drf-spectacular)
# =============================================================================

SPECTACULAR_SETTINGS = {
    'TITLE': 'SkillBridge API',
    'DESCRIPTION': 'Multi-sided opportunity marketplace connecting Talents, Organizations, Mentors, and Schools in Nigeria.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}


# =============================================================================
# PASSWORD VALIDATION
# =============================================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# =============================================================================
# INTERNATIONALIZATION
# =============================================================================

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Lagos'  # Nigerian timezone
USE_I18N = True
USE_TZ = True


# =============================================================================
# STATIC FILES
# =============================================================================

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise for efficient static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# =============================================================================
# DEFAULT PRIMARY KEY
# =============================================================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =============================================================================
# EMAIL CONFIGURATION
# =============================================================================
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
