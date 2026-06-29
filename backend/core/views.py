"""
Core taxonomy views — public read-only lists of Skills and Industries,
plus an authenticated POST /core/skills/ for user-suggested skills,
plus POST /core/uploads/sign/ to mint pre-signed Supabase upload URLs.
"""

import os
import uuid
from django.conf import settings
from django.utils.text import slugify
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import CanonicalIndustry, CanonicalSkill, Category
from .serializers import CanonicalIndustrySerializer, CanonicalSkillSerializer, CategorySerializer


class SkillListCreateView(APIView):
    """
    GET  /api/v1/core/skills/                  — all active skills (public)
    GET  /api/v1/core/skills/?category=Design  — filter by category
    GET  /api/v1/core/skills/?search=python    — case-insensitive name search
    POST /api/v1/core/skills/                  — auth required; find-or-create by name
    """
    def get_permissions(self):
        return [IsAuthenticated()] if self.request.method == 'POST' else [AllowAny()]

    def get(self, request):
        qs = CanonicalSkill.objects.filter(is_active=True).order_by('category', 'name')
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        if category:
            qs = qs.filter(category__iexact=category)
        if search:
            qs = qs.filter(name__icontains=search)
        return Response(CanonicalSkillSerializer(qs, many=True).data)

    def post(self, request):
        """
        Find-or-create. Lets users add new skills on the fly during onboarding
        / profile editing rather than being capped to the canonical list.

        Same-name (case-insensitive) collisions return the existing row — no
        duplicates. New rows default to category='Other' and is_active=True;
        admins can curate via Django admin later.
        """
        name = (request.data.get('name') or '').strip()
        if not name:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 400},
                 'errors': [{'field': 'name', 'message': 'Skill name is required.', 'code': 'required'}]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(name) > 100:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 400},
                 'errors': [{'field': 'name', 'message': 'Skill name too long (max 100 chars).',
                             'code': 'too_long'}]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Case-insensitive find-or-create
        existing = CanonicalSkill.objects.filter(name__iexact=name).first()
        if existing:
            return Response(CanonicalSkillSerializer(existing).data, status=status.HTTP_200_OK)

        # Generate a unique slug
        base_slug = slugify(name)[:90] or 'skill'
        slug = base_slug
        n = 2
        while CanonicalSkill.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{n}'
            n += 1

        skill = CanonicalSkill.objects.create(
            name=name, slug=slug,
            category=request.data.get('category', 'Other') or 'Other',
            is_active=True,
        )
        return Response(CanonicalSkillSerializer(skill).data, status=status.HTTP_201_CREATED)


class IndustryListView(APIView):
    """GET /api/v1/core/industries/  — all industries. Public."""
    permission_classes = [AllowAny]

    def get(self, request):
        qs = CanonicalIndustry.objects.all().order_by('name')
        return Response(CanonicalIndustrySerializer(qs, many=True).data)


class CategoryListView(APIView):
    """GET /api/v1/core/categories/  — all categories. Public."""
    permission_classes = [AllowAny]

    def get(self, request):
        qs = Category.objects.filter(is_active=True).order_by('name')
        return Response(CategorySerializer(qs, many=True).data)


# =============================================================================
# Pre-signed Supabase Storage upload URLs
# =============================================================================
# When `AWS_ACCESS_KEY_ID` is set, the backend can mint short-lived presigned
# PUT URLs that the browser uses to upload directly to Supabase Storage —
# the file bytes never touch the API server. Mirrors the ai_disabled /
# oauth_disabled pattern: when credentials are missing, returns 503.

ALLOWED_UPLOAD_PURPOSES = {
    # purpose: (folder_prefix, allowed_content_types, max_bytes)
    'avatar':      ('avatars',     {'image/png', 'image/jpeg', 'image/webp'},        2 * 1024 * 1024),
    'resume':      ('resumes',     {'application/pdf'},                              5 * 1024 * 1024),
    'org_logo':    ('org-logos',   {'image/png', 'image/jpeg', 'image/svg+xml',
                                    'image/webp'},                                   2 * 1024 * 1024),
    'school_logo': ('school-logos',{'image/png', 'image/jpeg', 'image/svg+xml',
                                    'image/webp'},                                   2 * 1024 * 1024),
}


class UploadSignView(APIView):
    """
    POST /api/v1/core/uploads/sign/

    Body: {
      "purpose":      "avatar" | "resume" | "org_logo" | "school_logo",
      "filename":     "selfie.png",
      "content_type": "image/png",
      "size":         12345  (optional, used for sanity-checking the max)
    }

    Returns: {
      "upload_url":  "https://...s3...?X-Amz-Signature=...",
      "public_url":  "https://<project>.supabase.co/storage/v1/object/public/<bucket>/<key>",
      "key":         "avatars/42/abc123.png",
      "expires_in":  300
    }

    The frontend PUTs the file bytes to `upload_url` with the same
    `Content-Type` header it declared here. Persist `public_url` on the
    relevant model (User.avatar_url, Application.resume_url, etc.).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not getattr(settings, 'USE_SUPABASE_STORAGE', False):
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 503, 'error_type': 'StorageDisabledError'},
                 'errors': [{'field': None,
                             'message': 'File uploads are not configured on this deployment.',
                             'code': 'storage_disabled'}]},
                status=503,
            )

        purpose = (request.data.get('purpose') or '').strip().lower()
        filename = (request.data.get('filename') or '').strip()
        content_type = (request.data.get('content_type') or '').strip()
        declared_size = request.data.get('size')

        if purpose not in ALLOWED_UPLOAD_PURPOSES:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 400},
                 'errors': [{'field': 'purpose',
                             'message': f'purpose must be one of: {sorted(ALLOWED_UPLOAD_PURPOSES.keys())}',
                             'code': 'invalid_purpose'}]},
                status=400,
            )

        folder, allowed_types, max_bytes = ALLOWED_UPLOAD_PURPOSES[purpose]

        if content_type not in allowed_types:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 400},
                 'errors': [{'field': 'content_type',
                             'message': f'{content_type or "missing"} is not allowed for {purpose}.',
                             'code': 'invalid_content_type'}]},
                status=400,
            )

        if declared_size is not None:
            try:
                if int(declared_size) > max_bytes:
                    return Response(
                        {'status': 'error', 'data': None,
                         'meta': {'http_status': 400},
                         'errors': [{'field': 'size',
                                     'message': f'File exceeds the {max_bytes // 1024 // 1024}MB limit for {purpose}.',
                                     'code': 'too_large'}]},
                        status=400,
                    )
            except (TypeError, ValueError):
                pass  # ignore non-numeric size; client may have omitted it

        # Build the object key. The user-id prefix keeps namespaces isolated
        # and lets you wipe a user's storage with a single prefix listing.
        ext = os.path.splitext(filename)[1].lower() or ''
        # Whitelist the extensions we'll honor; otherwise drop it.
        if ext and ext not in {'.png', '.jpg', '.jpeg', '.webp', '.svg', '.pdf'}:
            ext = ''
        key = f'{folder}/{request.user.id}/{uuid.uuid4().hex}{ext}'

        # Generate the presigned PUT URL via boto3.
        import boto3
        from botocore.config import Config

        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            endpoint_url=settings.AWS_S3_ENDPOINT_URL,
            region_name=getattr(settings, 'AWS_S3_REGION_NAME', 'auto'),
            config=Config(signature_version='s3v4'),
        )

        expires_in = 300  # 5 minutes
        try:
            upload_url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                    'Key': key,
                    'ContentType': content_type,
                },
                ExpiresIn=expires_in,
            )
        except Exception as exc:  # noqa: BLE001
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 502, 'error_type': type(exc).__name__},
                 'errors': [{'field': None,
                             'message': f'Failed to mint upload URL: {exc}',
                             'code': 'sign_failed'}]},
                status=502,
            )

        # Derive the public URL. Supabase exposes objects via
        # https://<project-ref>.supabase.co/storage/v1/object/public/<bucket>/<key>
        # when the bucket is public; otherwise the caller must use a signed
        # download URL. We assume public buckets for avatars/logos; resumes
        # may live in a private bucket — the frontend can decide whether to
        # store the public_url or generate a signed download URL on read.
        endpoint = (settings.AWS_S3_ENDPOINT_URL or '').rstrip('/')
        # endpoint looks like https://<ref>.supabase.co/storage/v1/s3
        # convert the trailing "/s3" to "/object/public/<bucket>/<key>"
        if endpoint.endswith('/s3'):
            base = endpoint[: -len('/s3')]
            public_url = f'{base}/object/public/{settings.AWS_STORAGE_BUCKET_NAME}/{key}'
        else:
            # Fall back to the s3-style URL; deployments using a different
            # endpoint shape can rewrite this on the frontend if needed.
            public_url = f'{endpoint}/{settings.AWS_STORAGE_BUCKET_NAME}/{key}'

        return Response({
            'upload_url': upload_url,
            'public_url': public_url,
            'key': key,
            'expires_in': expires_in,
        })
