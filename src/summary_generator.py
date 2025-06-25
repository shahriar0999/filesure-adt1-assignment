# ----------------------------
# Imports
# ----------------------------
import os
import json
import logging
from dotenv import load_dotenv
from openai import OpenAI

# ----------------------------
# Logging Configuration
# ----------------------------
logger = logging.getLogger("AuditorSummaryGenerator")
logger.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File handler
file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ----------------------------
# Load API Key
# ----------------------------
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    logger.error("No API key found. Please add it to your .env file.")
elif not api_key.startswith("sk-proj-"):
    logger.warning("API key may be incorrect — it should start with 'sk-proj-'")
elif api_key.strip() != api_key:
    logger.warning("API key appears to have extra whitespace. Please fix in .env file.")
else:
    logger.info("API key loaded successfully.")

openai = OpenAI()

# ----------------------------
# Prompts
# ----------------------------
system_prompt = """You are generating a formal and informative summary based on company filings disclosed via Form ADT-1. 
Your task is to write a 5–7 line summary of the auditor appointment in a clear, concise, and professional tone, suitable for business reporting or compliance documentation.

Use natural language similar to official press releases or statutory disclosures. Include key details such as the company name, auditor name, appointment period, form submission, and contact information.
"""

def user_prompt_for(path: str) -> str:
    try:
        with open(path, 'r') as file:
            data = json.load(file)
    except Exception as e:
        logger.error(f"Failed to load JSON from {path}: {e}")
        return ""

    user_prompt = f"""
You are reviewing a statutory disclosure submitted via Form ADT-1.

The following information was extracted from the document:

Company Name: {data['company_name']}
CIN: {data['cin']}
Registered Office: {data['registered_office']}
Company Email: {data['email_company']}

Auditor Appointment Details:
Auditor Name: {data['auditor_name']}
Auditor Address: {data['auditor_address']}
City: {data['auditor_city']}
State: {data['auditor_state']}
Auditor Email: {data['auditor_email']}
Auditor PAN: {data['auditor_pan']}
Number of Auditors Appointed: {data['number_of_auditors']}
Appointment Type: {data['appointment_type']}
Appointment Date: {data['appointment_date']}
Period of Appointment: From {data['appointment_period_from']} To {data['appointment_period_to']}

Task:
Write a short, professional summary in plain text describing this auditor appointment.
The summary should resemble the tone of a legal or regulatory announcement.
"""
    return user_prompt

def message(path: str):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(path)}
    ]

# ----------------------------
# Generate Summary
# ----------------------------
def generate_summary(path: str) -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=message(path),
            max_tokens=200,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return ""

# ----------------------------
# Main Execution
# ----------------------------
if __name__ == "__main__":
    input_path = "./data/processed/output.json"
    output_path = "./reports/summary.txt"

    summary = generate_summary(input_path)

    if summary:
        try:
            with open(output_path, "w", encoding="utf-8") as file:
                file.write(summary)
            logger.info(f"Summary successfully saved to: {output_path}")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")
    else:
        logger.warning("No summary was generated.")
