import logging
import fitz
import os
from typing import List, Dict

# logging configuration
logger = logging.getLogger("AttachmentParser")
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel('INFO')

file_handler = logging.FileHandler('errors.log')
file_handler.setLevel('ERROR')

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# name of the PDF file to be processed
input_file = "./data/raw/Form ADT-1-29092023_signed.pdf"

# Create output folder to save attachments files
output_dir = "./data/attachments"
os.makedirs(output_dir, exist_ok=True)

# load the pdf
def extract_attachments_from_pdf(file_path: str, output_dir: str) -> List[Dict]:
    extracted_files = []

    try:
        doc = fitz.open(file_path)
        count = doc.embfile_count()
    except Exception as e:
        logger.error(f"Error loading PDF file {file_path}: {e}")
        count = 0
    
    if count == 0:
        logger.warning(f"No attachments found in PDF file {file_path}.")
    
    else:
        logger.info(f"Found {count} attachments in PDF file {file_path}.")
        for i in range(count):
            try:
                info = doc.embfile_info(i)
                raw_name = info.get("filename", f"attachment_{i+1}")
                # Sanitize filename
                safe_name = "".join(c for c in raw_name if c.isalnum() or c in (' ', '.', '_', '-')).strip()
            except Exception as e:
                logger.error(f"Error retrieving metadata for attachment {i+1}: {e}")
                safe_name = f"attachment_{i+1}.pdf"

            try:
                # get data
                data = doc.embfile_get(i)

                # save the attachment
                output_path = os.path.join(output_dir, safe_name)
                with open(output_path, "wb") as f:
                    f.write(data)
                logger.info(f"Saved attachment {i+1} as {safe_name} in {output_dir}")

                extracted_files.append({
                        "filename": safe_name,
                        "size_bytes": len(data),
                        "path": output_path
                    })
            except Exception as e:
                logger.error(f"Error extracting attachment {i+1}: {e}")
            
    return extracted_files

if __name__ == "__main__":
    # Extract attachments from the specified PDF file
    files = extract_attachments_from_pdf(input_file, output_dir)
    logger.info(f"Extracted {len(files)} attachments from {input_file}.")
        









