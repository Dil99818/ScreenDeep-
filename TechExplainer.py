import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def explain_technologies(job_description):
    """Extract and explain all technologies/tools mentioned in the job description"""
    tech_results = {"explanations": "", "tech_list": []}

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": """You are a technology expert. Extract all tools, technologies, 
                frameworks, and platforms mentioned in the job description and provide concise one-line explanations."""},
                {"role": "user", "content": f"""Extract all technologies/tools from this job description and explain each in one line:

{job_description}

Format as:
**Technology/Tool:** Brief explanation (one line)

Example:
**Python:** Programming language for data science, web development, and automation
**Docker:** Containerization platform for application deployment and scaling

Focus on technical tools, programming languages, frameworks, databases, cloud platforms, and software."""}
            ],
            temperature=0.3
        )

        tech_results["explanations"] = response.choices[0].message.content
        tech_results["tech_list"] = extract_tech_list(response.choices[0].message.content)

    except Exception as e:
        tech_results["explanations"] = f"❌ Error analyzing technologies: {str(e)}"
        tech_results["tech_list"] = []

    return tech_results


def extract_tech_list(explanations_text):
    """Extract technology list from explanations for programmatic use"""
    import re

    tech_list = []

    # Pattern to match **Technology:** explanation format
    pattern = r'\*\*([^*]+):\*\*\s*([^\n]+)'
    matches = re.findall(pattern, explanations_text)

    for tech, explanation in matches:
        tech_list.append({
            "technology": tech.strip(),
            "explanation": explanation.strip()
        })

    return tech_list
