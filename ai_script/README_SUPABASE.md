# Supabase CV Comparison Script Documentation

## Overview
The `process_cv_supabase.py` script is designed to compare an input CV (in JSON format) against company requirements stored in a Supabase database. It uses the Gemini 3 AI model to perform semantic matching and updates the database to track which requirements have been compared.

## Configuration
The script requires the following environment variables to be set:

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Your Supabase Project URL. |
| `SUPABASE_KEY` | Your Supabase Service Role Key (or API Key). |
| `GEMINI_API_KEY` | Your Google Gemini API Key. |

## Database Schema Assumptions
The script currently assumes a table named `company_requirements` with at least the following columns:
- `id`: Unique identifier for the requirement.
- `requirement_details`: JSON or Text field containing the job/company requirements.
- `is_compared`: Boolean flag (default `False`) used to track processing status.

## Usage

### Direct Execution
You can run the script directly to test with a sample payload:
```bash
python process_cv_supabase.py
```

### Integration in Code
You can import the comparison function into your own application (e.g., an API endpoint):

```python
from process_cv_supabase import process_cv_comparison

# Your input payload (e.g., from a POST request)
cv_payload = {
    "name": "Jane Smith",
    "skills": ["React", "TypeScript", "Node.js"],
    "experience": "Senior Frontend Engineer"
}

# Run the comparison
matched_ids = process_cv_comparison(cv_payload)

print(f"Matched Requirement IDs: {matched_ids}")
```

## How It Works
1. **Fetch**: The script queries Supabase for all rows where `is_compared` is `False`.
2. **Analyze**: For each row, it sends the CV data and the requirement details to Gemini 3.
3. **Evaluate**: Gemini returns a JSON response indicating if it's a match and a brief reason.
4. **Update**: The script sets `is_compared = True` for the requirement in Supabase, regardless of whether it was a match.
5. **Report**: It returns a list of IDs for all requirements that were deemed a match.

## Output Format
The script returns a list of matching IDs:
`['uuid-1', 'uuid-2', ...]`
