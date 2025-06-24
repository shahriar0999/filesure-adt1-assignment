from pdf2image import convert_from_path
import pytesseract
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("No API key found! Please add OPENAI_API_KEY to your .env file.")
elif not api_key.startswith("sk-proj-"):
    print("API key does not start with 'sk-proj-'. Please check your API key.")
elif api_key.strip() != api_key:
    print("API key has leading or trailing spaces. Please remove them.")
else:
    print("API key loaded successfully.")

openai = OpenAI()

attachment_files_path = "./data/attachments"
report_output_path = "./reports/attachment_file_summary.md"

system_prompt = (
    "You are a helpful assistant designed to read and analyze the contents of scanned PDF documents. "
    "Each PDF file has been converted to plain text. Your task is to carefully read each document's content and generate "
    "a clear, concise summary for each one. Ignore repetitive formatting, page headers, or irrelevant boilerplate text. "
    "Focus only on meaningful content such as company names, appointment details, legal disclosures, auditor information, and dates. "
    "Present each PDF summary in well-structured markdown format, using clear headings and bullet points if necessary. "
    "Ensure that summaries are informative and sound professional."
)

def user_prompt_for_pdf_text_blocks(text: str) -> str:
    prompt = (
        "You are given the raw text extracted from a scanned PDF document. "
        "Your task is to generate a clear and professional markdown summary of the document. "
        "Focus on capturing:\n"
        "- Company names and CINs\n"
        "- Auditor details (name, PAN, email, address)\n"
        "- Appointment dates and periods\n"
        "- Declaration statements or official resolutions\n\n"
        "Ignore any headers, footers, page numbers, or repeated layout symbols.\n\n"
        "Here is the OCR-extracted text:\n\n"
    )
    prompt += text.strip()
    prompt += "\n\nReturn a structured markdown summary."
    return prompt

def generate_summary(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt_for_pdf_text_blocks(text)}
            ],
            max_tokens=500,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary: {e}")
        return None

def main():
    os.makedirs(os.path.dirname(report_output_path), exist_ok=True)
    summaries = {}

    for filename in sorted(os.listdir(attachment_files_path)):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(attachment_files_path, filename)
        print(f"Processing: {pdf_path}")

        # Convert PDF pages to images
        pages = convert_from_path(pdf_path, dpi=300)

        # Extract text from each page
        all_text_for_pdf = ""
        for i, page in enumerate(pages):
            page_text = pytesseract.image_to_string(page)
            all_text_for_pdf += f"\n\nPage {i + 1}:\n{page_text}"

        # Generate summary for this PDF
        summary = generate_summary(all_text_for_pdf)
        if summary:
            summaries[filename] = summary
            print(f"Summary for {filename} generated successfully.\n{'-'*50}\n")
        else:
            print(f"Failed to generate summary for {filename}\n{'-'*50}\n")

    # Save all summaries to a markdown file
    with open(report_output_path, "w", encoding="utf-8") as report_file:
        for fname, summ in summaries.items():
            report_file.write(f"# Summary for {fname}\n\n")
            report_file.write(summ + "\n\n---\n\n")

    print(f"All summaries saved to {report_output_path}")

if __name__ == "__main__":
    main()
