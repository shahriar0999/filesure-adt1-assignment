# imports
import os
import requests
from dotenv import load_dotenv
from openai import OpenAI
import json

# Load environment variables in a file called .env

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("No API key was found - please head over to the troubleshooting notebook in this folder to identify & fix!")
elif not api_key.startswith("sk-proj-"):
    print("An API key was found, but it doesn't start sk-proj-; please check you're using the right key - see troubleshooting notebook")
elif api_key.strip() != api_key:
    print("An API key was found, but it looks like it might have space or tab characters at the start or end - please remove them - see troubleshooting notebook")
else:
    print("API key found and looks good so far!")

openai = OpenAI()

def user_prompt_for(path):
    # load the data from the JSON file
    with open(path, 'r') as file:
        data = json.load(file)
    
    user_prompt = f"""\
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

Example:
“XYZ Pvt Ltd has appointed M/s Rao & Associates as its statutory auditor for FY 2023–24, effective from 1 July 2023. The appointment has been disclosed via Form ADT-1, with all supporting documents submitted.”

Use the above data to generate a similar summary.
"""
    return user_prompt


system_prompt = """ You are generating a formal and informative summary based on company filings disclosed via Form ADT-1. 
Your task is to write a 5–7 line summary of the auditor appointment in a clear, concise, and professional tone, suitable for business reporting or compliance documentation.

Use natural language similar to official press releases or statutory disclosures. Include key details such as the company name, auditor name, appointment period, form submission, and contact information.

Example tone:
“XYZ Pvt Ltd has appointed M/s Rao & Associates as its statutory auditor for FY 2023–24, effective from 1 July 2023. The appointment has been disclosed via Form ADT-1, with all supporting documents submitted.”"""


def message(path):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_for(path)}
    ]


def generate_summary(path):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=message(path),
            max_tokens=200,
            temperature=0.5
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

summary = generate_summary("./data/processed/output.json")

# save the summary to a file
if summary:
    with open("./reports/summary.txt", "w") as file:
        file.write(summary)
    print("Summary generated and saved to summary.txt")
