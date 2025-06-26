from openai import OpenAI
import os
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Long input text
long_text = """
OpenAI’s GPT-4 model is the latest in a series of large language models trained to understand and generate human-like text.
It can summarize, translate, answer questions, write stories, and perform many other language tasks. In addition, GPT-4 is multimodal, 
accepting both image and text inputs, making it a powerful general-purpose AI system. Organizations use GPT-4 across industries for automation, support, content creation, and more.
"""

# Prompt the model to summarize
response = client.chat.completions.create(
    model="gpt-4o",  # or "gpt-3.5-turbo" for a cheaper option
    messages=[
        {"role": "system", "content": "You are an expert summarizer."},
        {"role": "user", "content": f"Please summarize this text:\n\n{long_text}"}
    ],
    temperature=0.5
)

# Print the summary
summary = response.choices[0].message.content
print("Summary:\n", summary)
