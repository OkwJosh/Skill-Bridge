"""
School Views for SkillBridge API
================================

Endpoints for school admin and student data verification.
All responses use the standard JSON envelope.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import School, StudentRosterRecord
from .serializers import (
    SchoolSerializer,
    StudentRosterRecordSerializer,
    StudentRosterUploadSerializer,
    ConsentSerializer,
)
from talents.models import TalentProfile


class SchoolMeView(APIView):
    """
    GET /api/v1/schools/me/
    
    Returns the school profile for the logged-in school admin.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get the school(s) the current user administers."""
        user = request.user
        
        if not user.is_school_admin:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not a school admin.",
                    "code": "not_school_admin"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get schools this user administers
        schools = School.objects.filter(admins=user)
        
        if not schools.exists():
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "You are not assigned to any school.",
                    "code": "no_school"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Return first school (most users admin one school)
        # Can be extended to return multiple
        school = schools.first()
        serializer = SchoolSerializer(school)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"total_schools": schools.count()},
            "errors": []
        })


class SchoolRosterView(APIView):
    """
    GET /api/v1/schools/me/roster/
    POST /api/v1/schools/me/roster/
    
    GET: List student roster records for the school.
    POST: Add a new student roster record.
    """
    
    permission_classes = [IsAuthenticated]
    
    def _get_admin_school(self, user):
        """Helper to get school for admin user."""
        if not user.is_school_admin:
            return None, Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not a school admin.",
                    "code": "not_school_admin"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        school = School.objects.filter(admins=user).first()
        if not school:
            return None, Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "You are not assigned to any school.",
                    "code": "no_school"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        return school, None
    
    def get(self, request):
        """List roster records for the school."""
        school, error_response = self._get_admin_school(request.user)
        if error_response:
            return error_response
        
        # Optional filtering
        has_consented = request.query_params.get('has_consented')
        search = request.query_params.get('search')
        
        records = school.roster_records.all()
        
        if has_consented is not None:
            records = records.filter(has_consented=has_consented.lower() == 'true')
        
        if search:
            records = records.filter(
                matriculation_number__icontains=search
            ) | records.filter(
                full_name__icontains=search
            ) | records.filter(
                email__icontains=search
            )
        
        records = records.order_by('-created_at')
        serializer = StudentRosterRecordSerializer(records, many=True)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"count": len(serializer.data)},
            "errors": []
        })
    
    def post(self, request):
        """Add a student roster record."""
        school, error_response = self._get_admin_school(request.user)
        if error_response:
            return error_response
        
        serializer = StudentRosterUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        matric_number = serializer.validated_data['matriculation_number']
        
        # Check for duplicate
        if StudentRosterRecord.objects.filter(
            school=school,
            matriculation_number=matric_number
        ).exists():
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 409},
                "errors": [{
                    "field": "matriculation_number",
                    "message": "This matriculation number already exists in the roster.",
                    "code": "duplicate"
                }]
            }, status=status.HTTP_409_CONFLICT)
        
        record = StudentRosterRecord.objects.create(
            school=school,
            **serializer.validated_data
        )
        
        return Response({
            "status": "success",
            "data": StudentRosterRecordSerializer(record).data,
            "meta": {"message": "Student record added to roster."},
            "errors": []
        }, status=status.HTTP_201_CREATED)


class ConsentToSchoolDataView(APIView):
    """
    POST /api/v1/schools/consent/
    
    Allows a Talent to consent to sharing their school data.
    
    Flow:
    1. Talent provides their matriculation_number
    2. System finds matching StudentRosterRecord
    3. If found: sets has_consented=True, links talent_profile, sets is_school_verified=True
    4. Returns success with verified data
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Process consent to school data sharing."""
        user = request.user
        
        # Verify user is a talent
        if not user.is_talent:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "Only talents can consent to school data sharing.",
                    "code": "not_talent"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get talent profile
        try:
            talent_profile = user.talent_profile
        except TalentProfile.DoesNotExist:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 400},
                "errors": [{
                    "field": None,
                    "message": "Please create your talent profile first.",
                    "code": "no_profile"
                }]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = ConsentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        matric_number = serializer.validated_data['matriculation_number']
        school_id = serializer.validated_data.get('school_id')
        
        # Find matching roster record
        query = StudentRosterRecord.objects.filter(
            matriculation_number__iexact=matric_number
        )
        
        if school_id:
            query = query.filter(school_id=school_id)
        
        roster_record = query.first()
        
        if not roster_record:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": "matriculation_number",
                    "message": "No matching student record found. Please verify your matriculation number or contact your school.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if already consented by someone else
        if roster_record.has_consented and roster_record.talent_profile and roster_record.talent_profile != talent_profile:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 409},
                "errors": [{
                    "field": None,
                    "message": "This student record has already been claimed by another user.",
                    "code": "already_claimed"
                }]
            }, status=status.HTTP_409_CONFLICT)
        
        # Update roster record with consent
        roster_record.has_consented = True
        roster_record.consented_at = timezone.now()
        roster_record.talent_profile = talent_profile
        roster_record.save()
        
        # Update talent profile verification status
        talent_profile.is_school_verified = True
        talent_profile.verified_at = timezone.now()
        # Optionally update education info from roster
        if roster_record.course_of_study:
            talent_profile.field_of_study = roster_record.course_of_study
        if roster_record.school.name:
            talent_profile.institution_name = roster_record.school.name
        if roster_record.graduation_year or roster_record.expected_graduation_year:
            talent_profile.graduation_year = roster_record.graduation_year or roster_record.expected_graduation_year
        talent_profile.save()
        
        return Response({
            "status": "success",
            "data": {
                "verified": True,
                "school_name": roster_record.school.name,
                "matriculation_number": roster_record.matriculation_number,
                "course_of_study": roster_record.course_of_study,
                "department": roster_record.department,
                "is_graduated": roster_record.is_graduated,
            },
            "meta": {"message": "Your academic records have been verified successfully!"},
            "errors": []
        })


class VerificationStatusView(APIView):
    """
    GET /api/v1/schools/verification-status/
    
    Check if the current talent's academic records are verified.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get verification status for current user."""
        user = request.user
        
        if not user.is_talent:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "Only talents can check verification status.",
                    "code": "not_talent"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            talent_profile = user.talent_profile
        except TalentProfile.DoesNotExist:
            return Response({
                "status": "success",
                "data": {
                    "is_verified": False,
                    "has_profile": False,
                },
                "meta": {},
                "errors": []
            })
        
        # Get linked school record if any
        school_record = StudentRosterRecord.objects.filter(
            talent_profile=talent_profile,
            has_consented=True
        ).select_related('school').first()
        
        data = {
            "is_verified": talent_profile.is_school_verified,
            "has_profile": True,
            "verified_at": talent_profile.verified_at,
        }
        
        if school_record:
            data["school_name"] = school_record.school.name
            data["course_of_study"] = school_record.course_of_study
            data["is_graduated"] = school_record.is_graduated
        
        return Response({
            "status": "success",
            "data": data,
            "meta": {},
            "errors": []
        })

