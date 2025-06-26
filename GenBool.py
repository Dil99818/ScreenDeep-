# GenBool.py - Boolean Query Generation Module
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_boolean(job_description):
    """Generate multiple boolean search strategies"""
    boolean_results = {"boolean_string": "", "multiple_queries": {}}

    try:
        # Generate comprehensive boolean queries
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are an expert Boolean search specialist for resume screening. 
                Generate multiple search strategies for different recruitment needs."""},
                {"role": "user", "content": f"""Based on this job description, generate 5 different Boolean search strings:

{job_description}

Provide:
1. **Final-Search** - generate a comprehensive Boolean search string suitable for sourcing candidates on LinkedIn or job boards.
(Include all key technical skills, programming languages, frameworks, and relevant job titles.
Use synonyms and alternative job titles where appropriate.
Exclude unrelated roles if possible.
Format the Boolean string for use in a resume database or LinkedIn search.
include all must have & nice to have tools/technology


2. **Broad Search** - only include must-have & nice to have tools/technologies mentioned in the job description. Exclude soft skills or optional items.
without job title. 
Use "OR" for synonyms, alternative and Semantic similarity
Use "AND" for must-have & nice to tools/technologies
Format the Boolean string for use in a resume database like Monster, Dice, Indeed or LinkedIn search.


3. **Targeted Search** - Balanced approach (mix of AND/OR)  
4. **Strict Search** - Only highly qualified candidates (AND-heavy)
5. **Skills-Only Search** - Focus purely on technical skills



Format each as:
**[Search Type]:**
[actual boolean string]

**Use Case**: [when to use this search]

Do NOT include location, years of experience, or company names in the boolean strings."""}
            ],
            temperature=0.3
        )

        boolean_results["boolean_string"] = response.choices[0].message.content

        # Extract individual queries for programmatic use
        boolean_results["multiple_queries"] = extract_boolean_queries(response.choices[0].message.content)

    except Exception as e:
        boolean_results["boolean_string"] = f"❌ Error generating Boolean: {str(e)}"
        boolean_results["multiple_queries"] = {}

    return boolean_results


def generate_simple_boolean(job_description):
    """Generate a simple boolean query (backward compatibility)"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an expert recruiter and Boolean search expert."},
                {"role": "user", "content": f"""Generate a balanced Boolean search string using AND/OR operators based on this job description. 
                Focus on the most important skills and requirements.
                Do not include location or years of experience:

{job_description}"""}
            ],
            temperature=0.3
        )
        return {"boolean_string": response.choices[0].message.content}
    except Exception as e:
        return {"boolean_string": f"❌ Error generating Boolean: {str(e)}"}


def extract_boolean_queries(boolean_text):
    """Extract individual boolean queries from the generated text"""
    import re

    queries = {}

    # Pattern to match each search type
    search_types = ["Final-Search", "Broad Search", "Targeted Search", "Strict Search", "Skills-Only Search"]

    for search_type in search_types:
        pattern = f"\\*\\*{search_type}:\\*\\*(.*?)(?=\\*\\*|$)"
        match = re.search(pattern, boolean_text, re.DOTALL)

        if match:
            content = match.group(1).strip()
            # Extract the actual boolean query
            query_match = re.search(r'Boolean Query:\s*(.+)', content)
            use_case_match = re.search(r'Use Case:\s*(.+)', content)

            queries[search_type.lower().replace(" ", "_")] = {
                "query": query_match.group(1).strip() if query_match else "",
                "use_case": use_case_match.group(1).strip() if use_case_match else ""
            }

    return queries
