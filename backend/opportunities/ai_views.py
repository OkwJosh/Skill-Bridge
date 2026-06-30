
import os
import google.generativeai as genai
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class GenerateDescriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get('prompt', '')
        if not prompt:
            return Response({'message': 'Prompt is required'}, status=400)
            
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return Response({'message': 'AI integration is not configured'}, status=500)
            
        genai.configure(api_key=api_key)
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            full_prompt = (
                f'Act as a professional technical recruiter. '
                f'Generate a highly professional, engaging job description for an internship or project opportunity '
                f'based on the following prompt: \n\n{prompt}\n\n'
                f'Output only the job description in plain text or markdown without any conversational filler.'
            )
            response = model.generate_content(full_prompt)
            description = response.text.strip()
            return Response({'status': 'success', 'data': {'description': description}})
        except Exception as e:
            return Response({'status': 'error', 'errors': [{'message': f'Failed to generate description: {str(e)}'}]}, status=500)


from opportunities.models import Application

class ScreenApplicationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            application = Application.objects.select_related('opportunity', 'talent', 'talent__user').get(pk=pk)
        except Application.DoesNotExist:
            return Response({'message': 'Application not found'}, status=404)
            
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return Response({'message': 'AI integration is not configured'}, status=500)
            
        genai.configure(api_key=api_key)
        
        opp_desc = application.opportunity.description
        talent_skills = ', '.join([s.skill.name for s in application.talent.skills.all()])
        talent_bio = application.talent.bio
        
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            prompt = (
                f'Act as a technical recruiter. Screen the following candidate against the job description.\n'
                f'Job Description:\n{opp_desc}\n\n'
                f'Candidate Bio: {talent_bio}\n'
                f'Candidate Skills: {talent_skills}\n\n'
                f'Provide a match score out of 100, followed by a brief 2-sentence summary of why they are or are not a good fit. '
                f'Format EXACTLY like this:\n'
                f'Score: 85\n'
                f'Summary: [Your 2 sentence summary here]'
            )
            response = model.generate_content(prompt)
            text = response.text.strip()
            
            # Parse response
            lines = text.split('\n')
            score = 0
            summary = ''
            for line in lines:
                if line.startswith('Score:'):
                    try:
                        score = int(line.replace('Score:', '').strip())
                    except:
                        pass
                elif line.startswith('Summary:'):
                    summary = line.replace('Summary:', '').strip()
            
            if not summary and len(lines) > 0:
                summary = text # Fallback
                
            return Response({
                'score': score,
                'summary': summary
            })
        except Exception as e:
            return Response({'message': f'Failed to screen candidate: {str(e)}'}, status=500)

