"""
School Models for SkillBridge
=============================

Schools act as a Data Trust to verify academic records.
Students can consent to share their data for verification.
"""

from django.db import models
from django.conf import settings


class School(models.Model):
    """
    University, Polytechnic, or Bootcamp registered as a Data Trust.
    
    School admins can:
    - Upload student rosters
    - Verify student academic records
    """
    
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    
    # Type
    school_type = models.CharField(
        max_length=20,
        choices=[
            ('university', 'University'),
            ('polytechnic', 'Polytechnic'),
            ('bootcamp', 'Bootcamp'),
            ('other', 'Other'),
        ],
        default='university'
    )
    
    # Contact
    website_url = models.URLField(blank=True)
    contact_email = models.EmailField(blank=True)
    
    # Location
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Nigeria')
    
    # Verification
    is_verified = models.BooleanField(
        default=False,
        help_text="School has been verified by SkillBridge"
    )
    
    # Admins (users who can manage this school)
    admins = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='administered_schools',
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'schools'
        ordering = ['name']
        verbose_name = 'School'
        verbose_name_plural = 'Schools'
    
    def __str__(self):
        return f"{self.name} ({self.school_type})"


class StudentRosterRecord(models.Model):
    """
    Pre-uploaded student data from a School.
    
    Used for verification:
    1. School admin uploads roster with matriculation numbers
    2. Student/Talent provides consent by entering their matric number
    3. System matches and verifies the talent's academic record
    """
    
    school = models.ForeignKey(
        School,
        on_delete=models.CASCADE,
        related_name='roster_records'
    )
    
    # Student Identification
    matriculation_number = models.CharField(
        max_length=50,
        db_index=True,
        help_text="Student's matriculation/registration number"
    )
    
    # Student Info (from school records)
    email = models.EmailField(
        blank=True,
        help_text="Student's school email"
    )
    
    full_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Student's name as per school records"
    )
    
    department = models.CharField(
        max_length=200,
        blank=True,
        help_text="Department/Faculty"
    )
    
    course_of_study = models.CharField(
        max_length=200,
        blank=True,
        help_text="Course/Program of study"
    )
    
    enrollment_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year of enrollment"
    )
    
    expected_graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True
    )
    
    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Actual graduation year (if graduated)"
    )
    
    is_graduated = models.BooleanField(default=False)
    
    # CGPA (optional, schools may choose not to share)
    cgpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Cumulative GPA if school provides it"
    )
    
    # Consent Management
    has_consented = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Student has consented to data sharing"
    )
    
    consented_at = models.DateTimeField(
        null=True,
        blank=True
    )
    
    # Link to TalentProfile (set when consent is given)
    talent_profile = models.ForeignKey(
        'talents.TalentProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='school_records'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_roster_records'
        unique_together = ['school', 'matriculation_number']
        verbose_name = 'Student Roster Record'
        verbose_name_plural = 'Student Roster Records'
    
    def __str__(self):
        return f"{self.matriculation_number} - {self.school.name}"

