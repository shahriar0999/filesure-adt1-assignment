# ----------------------------------------
# Imports
# ----------------------------------------
import os
import logging
from dotenv import load_dotenv
from openai import OpenAI
from pdf2image import convert_from_path
import pytesseract

# ----------------------------------------
# Logging Configuration
# ----------------------------------------
logger = logging.getLogger("AttachmentSummary")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# ----------------------------------------
# Load API Key
# ----------------------------------------
load_dotenv(override=True)
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    logger.error("No API key found. Please add OPENAI_API_KEY to your .env file.")
elif not api_key.startswith("sk-proj-"):
    logger.warning("API key does not start with 'sk-proj-'. Check your credentials.")
elif api_key.strip() != api_key:
    logger.warning("API key has leading or trailing whitespace. Please remove them.")
else:
    logger.info("API key loaded successfully.")

openai = OpenAI()

# ----------------------------------------
# Paths and Prompts
# ----------------------------------------
attachment_files_path = "./data/attachments"
report_output_path = "./reports/attachment_file_summary.md"
os.makedirs(os.path.dirname(report_output_path), exist_ok=True)

# System Prompt for LLM
system_prompt = (
    "You are a helpful assistant designed to read and analyze the contents of scanned PDF documents. "
    "Each PDF file has been converted to plain text. Your task is to carefully read each document's content and generate "
    "a clear, concise summary for each one. Ignore repetitive formatting, page headers, or irrelevant boilerplate text. "
    "Focus only on meaningful content such as company names, appointment details, legal disclosures, auditor information, and dates. "
    "Present each PDF summary in well-structured markdown format, using clear headings and bullet points if necessary. "
    "Ensure that summaries are informative and sound professional."
)

# User Prompt Generator
def user_prompt_for_pdf_text_blocks(text: str) -> str:
    return (
        "You are given the raw text extracted from a scanned PDF document. "
        "Your task is to generate a clear and professional markdown summary of the document.\n\n"
        "Focus on capturing:\n"
        "- Company names and CINs\n"
        "- Auditor details (name, PAN, email, address)\n"
        "- Appointment dates and periods\n"
        "- Declaration statements or official resolutions\n\n"
        "Ignore any headers, footers, page numbers, or repeated layout symbols.\n\n"
        "Here is the OCR-extracted text:\n\n"
        f"{text.strip()}\n\nReturn a structured markdown summary."
    )

# ----------------------------------------
# Function to Generate Summary using OpenAI
# ----------------------------------------
def generate_summary(text: str) -> str:
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_pdf_text_blocks(text)}
            ],
            max_tokens=500,
            temperature=0.2
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return None

# ----------------------------------------
# Main Function
# ----------------------------------------
def main():
    summaries = {}

    for filename in sorted(os.listdir(attachment_files_path)):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(attachment_files_path, filename)
        logger.info(f"Processing: {pdf_path}")

        try:
            pages = convert_from_path(pdf_path, dpi=300)
        except Exception as e:
            logger.error(f"Error converting {filename} to images: {e}")
            continue

        # Extract text from all pages
        all_text = ""
        for i, page in enumerate(pages):
            try:
                page_text = pytesseract.image_to_string(page)
                all_text += f"\n\nPage {i + 1}:\n{page_text}"
            except Exception as e:
                logger.error(f"Error reading page {i + 1} of {filename}: {e}")

        # Generate summary
        summary = generate_summary(all_text)
        if summary:
            summaries[filename] = summary
            logger.info(f"Summary for {filename} generated successfully.")
        else:
            logger.warning(f"Summary for {filename} could not be generated.")

    # Save summaries to markdown file
    try:
        with open(report_output_path, "w", encoding="utf-8") as file:
            for fname, summ in summaries.items():
                file.write(f"# Summary for {fname}\n\n{summ}\n\n---\n\n")
        logger.info(f"All summaries saved to: {report_output_path}")
    except Exception as e:
        logger.error(f"Error saving report: {e}")

# ----------------------------------------
# Entry Point
# ----------------------------------------
if __name__ == "__main__":
    main()
