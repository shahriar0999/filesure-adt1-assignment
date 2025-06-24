from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import re
import json


# PDF file path
pdf_path = "./data/raw/Form ADT-1-29092023_signed.pdf"

# Convert PDF pages to images
pages = convert_from_path(pdf_path, dpi=300)


# Step 5: Extract text from each page
all_text = ""
for i, page in enumerate(pages):
    text = pytesseract.image_to_string(page)
    all_text += f"\n\n📄 Page {i+1}:\n{text}"


def extract_adt1_fields(text: str):
    def match_or_default(pattern, default=""):
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else default

    extracted = {
        # Company Name (all caps, ends with PRIVATE LIMITED)
        "company_name": match_or_default(
            r"\*?\s*Name of the company\s+([A-Z &\-]+PRIVATE LIMITED)"
        ),

        # CIN
        "cin": match_or_default(
            r"(?i)corporate identity number\s*\(CIN\)\s*of company\s+([A-Z0-9]+)"
        ),

        # Registered Office Address (captures up to PIN)
        "registered_office": match_or_default(
            r"Address of the registered office\s+(.*?)(\d{6})", ""
        ).replace("of the company", "").replace("\n", ", ").strip(),

        "email_company": match_or_default(r"\*?email id of the company\s+([\w\.-]+@[\w\.-]+)"),

        # Auditor Name
        "auditor_name": match_or_default(
            r"(?i)\*?\s*Name of the auditor or auditor's firm\s+([A-Z &]+)"
        ),

        # Auditor Membership Number (if available)
        "number_of_auditors": match_or_default(r"Number of auditor\(s\) appointed\s+(\d+)"),

        # Auditor Address (from line under “Address of Auditor” up to *City or *State)
        "auditor_address": match_or_default(
            r"\*?\s*Address of the Auditor.*?\n+(.+?)(?=\n\s*\*City|\n\s*\*State)"
        ).replace("\n", ", ").strip(),

    
        "auditor_address": match_or_default(r"Address of the Auditor.*?\n(?:or auditor's firm)?\s*\n(.*?\n.*?)(?=\*City)", ).replace("\n", ", ").strip(),

        "auditor_city": match_or_default(r"\*City\s+([A-Za-z ]+)"),
        "auditor_state": match_or_default(r"\*State\s+([A-Za-z\-]+)"),
        "auditor_email": match_or_default(r"email id of the auditor\s*:?\s*(?:.*?\n)?or auditor's firm\s+([\w\.-]+@[\w\.-]+)"),

        "auditor_pan": match_or_default(r"permanent account number of auditor.*?([A-Z0-9]{10})"),

        "appointment_period_from": match_or_default(r"From\s+(?:lo1|l01|01|1o1|[l1oO]{2,3})[/\-]?(\d{2}/\d{4})"),

        "appointment_period_to": match_or_default(r"To\s+(\d{2}/\d{2}/\d{4})"),


        # Appointment Date
        "appointment_date": match_or_default(
            r"(?i)\b(?:date of AGM|Date of appointment)\s+(\d{2}/\d{2}/\d{4})"),

        # Appointment Type (Appointment or Re-appointment)
        "appointment_type": match_or_default(r"Nature of appointment\s+\[?([A-Za-z\- /]+)"),
    }

    return extracted

# call the function to extract fields from the text which is extracted from the pdf
result = extract_adt1_fields(all_text)  

# save this result as json file
with open("./data/processed/output.json", "w") as f:
    json.dump(result, f, indent=4)

