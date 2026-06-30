import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import TalentProfile
from opportunities.models import Opportunity

def get_gemini_model():
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-2.5-flash')

class GenerateBioView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response({'message': 'Prompt/bullet points are required'}, status=400)
            
        model = get_gemini_model()
        if not model:
            return Response({'message': 'AI integration is not configured'}, status=500)
            
        try:
            full_prompt = (
                f'Act as a professional career coach and resume writer. '
                f'Generate a concise, professional bio/summary for a talent profile based on the following notes: \n\n{prompt}\n\n'
                f'Output only the bio text without conversational filler.'
            )
            response = model.generate_content(full_prompt)
            return Response({'status': 'success', 'data': {'bio': response.text.strip()}})
        except Exception as e:
            return Response({'status': 'error', 'errors': [{'message': f'Failed to generate bio: {str(e)}'}]}, status=500)


class GenerateCoverLetterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        opportunity_id = request.data.get('opportunity_id')
        if not opportunity_id:
            return Response({'message': 'opportunity_id is required'}, status=400)
            
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
        except Opportunity.DoesNotExist:
            return Response({'message': 'Opportunity not found'}, status=404)
            
        try:
            talent = TalentProfile.objects.get(user=request.user)
        except TalentProfile.DoesNotExist:
            return Response({'message': 'Talent profile not found'}, status=404)
            
        model = get_gemini_model()
        if not model:
            return Response({'message': 'AI integration is not configured'}, status=500)
            
        talent_skills = ', '.join([s.skill.name for s in talent.skills.all()])
        
        try:
            full_prompt = (
                f'Act as a professional career coach. Write a tailored, persuasive cover letter for this candidate applying to this job.\n\n'
                f'Job Title: {opportunity.title}\n'
                f'Job Description: {opportunity.description}\n\n'
                f'Candidate Name: {request.user.full_name}\n'
                f'Candidate Bio: {talent.bio}\n'
                f'Candidate Skills: {talent_skills}\n\n'
                f'Output only the cover letter text.'
            )
            response = model.generate_content(full_prompt)
            return Response({'status': 'success', 'data': {'cover_letter': response.text.strip()}})
        except Exception as e:
            return Response({'status': 'error', 'errors': [{'message': f'Failed to generate cover letter: {str(e)}'}]}, status=500)


class GenerateInterviewPrepView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        opportunity_id = request.data.get('opportunity_id')
        if not opportunity_id:
            return Response({'message': 'opportunity_id is required'}, status=400)
            
        try:
            opportunity = Opportunity.objects.get(id=opportunity_id)
        except Opportunity.DoesNotExist:
            return Response({'message': 'Opportunity not found'}, status=404)
            
        model = get_gemini_model()
        if not model:
            return Response({'message': 'AI integration is not configured'}, status=500)
            
        try:
            full_prompt = (
                f'Act as a professional career coach and technical interviewer. '
                f'Based on the following job description, generate 3-5 likely interview questions the candidate might be asked, '
                f'along with brief tips on how to answer each one.\n\n'
                f'Job Title: {opportunity.title}\n'
                f'Job Description: {opportunity.description}\n\n'
                f'Output in a clean, readable markdown format.'
            )
            response = model.generate_content(full_prompt)
            return Response({'status': 'success', 'data': {'interview_prep': response.text.strip()}})
        except Exception as e:
            return Response({'status': 'error', 'errors': [{'message': f'Failed to generate interview prep: {str(e)}'}]}, status=500)


class GenerateResumeSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            talent = TalentProfile.objects.get(user=request.user)
        except TalentProfile.DoesNotExist:
            return Response({'message': 'Talent profile not found'}, status=404)
            
        model = get_gemini_model()
        if not model:
            return Response({'message': 'AI integration is not configured'}, status=500)
            
        talent_skills = ', '.join([s.skill.name for s in talent.skills.all()])
        
        try:
            full_prompt = (
                f'Act as an expert resume writer. Take the following candidate profile details and generate a '
                f'powerful, professional resume summary section (1-2 short paragraphs) that highlights their strengths.\n\n'
                f'Candidate Bio: {talent.bio}\n'
                f'Candidate Skills: {talent_skills}\n\n'
                f'Output only the resume summary text.'
            )
            response = model.generate_content(full_prompt)
            return Response({'status': 'success', 'data': {'resume_summary': response.text.strip()}})
        except Exception as e:
            return Response({'status': 'error', 'errors': [{'message': f'Failed to generate resume summary: {str(e)}'}]}, status=500)
