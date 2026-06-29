import os
import json
from supabase import create_client, Client
from google import genai
from google.genai import types

# --- 2026 CONFIGURATION ---
MODEL_NAME = 'gemini-3-flash-preview'

# Initialize Supabase
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Initialize Gemini 3
client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))

SYSTEM_PROMPT = """
Compare the input CV (JSON) against the provided Company Requirement.
Determine if the CV matches the requirements.
Return a JSON object with:
1. "is_match": boolean
2. "reason": a brief explanation (1 sentence)
Output MUST be a single JSON object.
"""

def process_cv_comparison(cv_data: dict):
    """
    Compares an input CV against uncompared requirements in Supabase.
    Returns a list of IDs of matching requirements.
    """
    matched_ids = []
    
    # 1. Fetch uncompared requirements
    # Assuming the table is 'company_requirements' and the flag is 'is_compared'
    response = supabase.table('company_requirements').select('id, requirement_details').eq('is_compared', False).execute()
    
    requirements = response.data
    
    if not requirements:
        print("No uncompared requirements found.")
        return []

    print(f"Comparing CV against {len(requirements)} requirements...")

    for req in requirements:
        req_id = req['id']
        req_details = req['requirement_details']

        # 2. Compare using Gemini
        try:
            prompt = f"CV Data: {json.dumps(cv_data)}\n\nRequirement: {json.dumps(req_details)}"
            
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type='application/json'
                )
            )
            
            result = json.loads(response.text)
            
            if result.get('is_match'):
                matched_ids.append(req_id)
                print(f"Match found for Requirement ID: {req_id}")
            else:
                print(f"No match for Requirement ID: {req_id}")

            # 3. Mark as compared in Supabase
            supabase.table('company_requirements').update({'is_compared': True}).eq('id', req_id).execute()

        except Exception as e:
            print(f"Error processing requirement {req_id}: {e}")

    return matched_ids

if __name__ == "__main__":
    # Example input placeholder
    sample_cv = {
        "name": "John Doe",
        "skills": ["Python", "SQL", "Cloud Computing"],
        "experience": "5 years in backend development"
    }
    
    results = process_cv_comparison(sample_cv)
    print(f"Comparison complete. Matched Requirement IDs: {results}")
