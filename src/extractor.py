from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import re
import json
import logging

# ----------------------------
# Logging Configuration
# ----------------------------

logger = logging.getLogger("Extract-Structured-Information")
logger.setLevel(logging.INFO)

# Console log (for general updates)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# File log (only logs errors)
file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)

# Formatter for log messages
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


# ----------------------------
# PDF Processing
# ----------------------------

# Path to the ADT-1 PDF file
pdf_path = "./data/raw/Form ADT-1-29092023_signed.pdf"

logger.info("Starting PDF to image conversion...")

try:
    # Convert all PDF pages to high-res images
    pages = convert_from_path(pdf_path, dpi=300)
    logger.info(f"Successfully converted {len(pages)} pages from PDF.")
except Exception as e:
    logger.error(f"Error converting PDF to images: {e}")
    raise

# Extract text from each image using OCR
all_text = ""
for i, page in enumerate(pages):
    try:
        text = pytesseract.image_to_string(page)
        all_text += f"\n\n📄 Page {i+1}:\n{text}"
        logger.info(f"Text extracted from page {i+1}")
    except Exception as e:
        logger.error(f"Error extracting text from page {i+1}: {e}")


# ----------------------------
# Regex-Based Field Extraction
# ----------------------------

def extract_adt1_fields(text: str):
    """Extracts structured information from OCR text using regular expressions."""
    
    def match_or_default(pattern, default=""):
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else default

    extracted = {
        # Company name (assumes uppercase + PRIVATE LIMITED)
        "company_name": match_or_default(
            r"\*?\s*Name of the company\s+([A-Z &\-]+PRIVATE LIMITED)"
        ),

        # Corporate Identity Number (CIN)
        "cin": match_or_default(
            r"(?i)corporate identity number\s*\(CIN\)\s*of company\s+([A-Z0-9]+)"
        ),

        # Registered Office Address
        "registered_office": match_or_default(
            r"Address of the registered office\s+(.*?)(\d{6})", ""
        ).replace("of the company", "").replace("\n", ", ").strip(),

        # Company email
        "email_company": match_or_default(
            r"\*?email id of the company\s+([\w\.-]+@[\w\.-]+)"
        ),

        # Auditor name
        "auditor_name": match_or_default(
            r"(?i)\*?\s*Name of the auditor or auditor's firm\s+([A-Z &]+)"
        ),

        # Number of auditors
        "number_of_auditors": match_or_default(
            r"Number of auditor\(s\) appointed\s+(\d+)"
        ),

        # Full auditor address (up to *City)
        "auditor_address": match_or_default(
            r"Address of the Auditor.*?\n(?:or auditor's firm)?\s*\n(.*?\n.*?)(?=\*City)"
        ).replace("\n", ", ").strip(),

        # Auditor city and state
        "auditor_city": match_or_default(r"\*City\s+([A-Za-z ]+)"),
        "auditor_state": match_or_default(r"\*State\s+([A-Za-z\-]+)"),

        # Auditor email
        "auditor_email": match_or_default(
            r"email id of the auditor\s*:?\s*(?:.*?\n)?or auditor's firm\s+([\w\.-]+@[\w\.-]+)"
        ),

        # Auditor PAN (10-character alphanumeric)
        "auditor_pan": match_or_default(
            r"permanent account number of auditor.*?([A-Z0-9]{10})"
        ),

        # Period of appointment (from and to)
        "appointment_period_from": match_or_default(
            r"From\s+(?:lo1|l01|01|1o1|[l1oO]{2,3})[/\-]?(\d{2}/\d{4})"
        ),
        "appointment_period_to": match_or_default(
            r"To\s+(\d{2}/\d{2}/\d{4})"
        ),

        # Date of appointment (AGM)
        "appointment_date": match_or_default(
            r"(?i)\b(?:date of AGM|Date of appointment)\s+(\d{2}/\d{2}/\d{4})"
        ),

        # Type of appointment
        "appointment_type": match_or_default(
            r"Nature of appointment\s+\[?([A-Za-z\- /]+)"
        ),
    }

    return extracted


# ----------------------------
# Save Extracted Result to JSON
# ----------------------------

logger.info("Starting extraction of structured fields from text...")


def main():
    try:
        result = extract_adt1_fields(all_text)
        output_path = "./data/processed/output.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)

        logger.info(f"Extracted data saved to: {output_path}")
    except Exception as e:
        logger.error(f"Failed to extract or save structured data: {e}")

if __name__ == "__main__":
    main()