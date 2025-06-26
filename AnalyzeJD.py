# AnalyzeJD.py - Job Description Analysis Module
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_job_description(job_description):
    """Generates summary and structured analysis from a job description using OpenAI"""
    jd_results = {"summary": "", "structured_data": {}}

    # Generate Enhanced Summary
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are an expert job description analyzer. 
                Provide a clear, structured analysis including:
                1. Executive summary (2-3 sentences)
                2. Must-have skills (list them clearly)
                3. Nice-to-have skills
                
                4. Experience level required"""},
                {"role": "user", "content": f"""Analyze this job description and provide structured output:

{job_description}

Format your response clearly with sections:
**Summary:**
1.Try to summarize the job description into a concise summary:
2.The summary should be no more than 2–3 lines.
3.If available, include details about the industry, project background, and key responsibilities of the role.
4.Avoid listing skills or technologies — focus on what the role is about and its overall purpose.

**Must-Have Skills:**
1.Should be no more than 3 lines.
2.pls listing tools & technology 
3.Mention Required Qualifications & minimum years of experience 

**Nice-to-Have Skills:**
1. Should be no more than 3 lines.

**"Tools & technology required**
Extract technologies from the job description and categorize them under appropriate headings like:
Programming Languages
Cloud Platforms (e.g., AWS, Azure)
AWS Networking & Delivery Services
Monitoring & Logging Tools
CI/CD Tools
Databases
DevOps & Infrastructure Tools
Machine Learning or Data Engineering Tools

**Experience Required:**
[Experience level]"""}
            ],
            temperature=0.3
        )
        jd_results["summary"] = response.choices[0].message.content

        # Extract structured data
        jd_results["structured_data"] = extract_structured_data(response.choices[0].message.content)

    except Exception as e:
        jd_results["summary"] = f"❌ Error generating analysis: {str(e)}"
        jd_results["structured_data"] = {}

    return jd_results


def extract_structured_data(analysis_text):
    """Extract structured data from analysis for programmatic use"""
    import re
    from datetime import datetime

    structured_data = {
        "timestamp": datetime.now().isoformat(),
        "must_have_skills": [],
        "nice_to_have_skills": [],
        "experience_level": "",
        "summary": ""
    }

    # Extract must-have skills
    must_have_match = re.search(r'\*\*Must-Have Skills:\*\*(.*?)(?=\*\*|$)', analysis_text, re.DOTALL)
    if must_have_match:
        skills = re.findall(r'- (.+)', must_have_match.group(1))

        structured_data["must_have_skills"] = [skill.strip() for skill in skills]

    # Extract nice-to-have skills
    nice_to_have_match = re.search(r'\*\*Nice-to-Have Skills:\*\*(.*?)(?=\*\*|$)', analysis_text, re.DOTALL)
    if nice_to_have_match:
        skills = re.findall(r'- (.+)', nice_to_have_match.group(1))
        structured_data["nice_to_have_skills"] = [skill.strip() for skill in skills]

    # Extract summary
    summary_match = re.search(r'\*\*Summary:\*\*(.*?)(?=\*\*|$)', analysis_text, re.DOTALL)
    if summary_match:
        structured_data["summary"] = summary_match.group(1).strip()

    # Extract experience
    exp_match = re.search(r'\*\*Experience Required:\*\*(.*?)(?=\*\*|$)', analysis_text, re.DOTALL)
    if exp_match:
        structured_data["experience_level"] = exp_match.group(1).strip()

    return structured_data