# ADT-1 PDF Extraction Report

## Objective  
The goal of this task was to extract key information from the Form ADT-1 PDF, such as company name, CIN, registered office, and auditor details. We started by using common Python libraries to parse the document.

## Approach  
Initially, libraries like PyMuPDF and pdfplumber were used to extract text directly from the PDF. While some fields like the company name and auditor’s name were partially retrievable, most of the content had layout inconsistencies and non-standard formatting. This made it difficult to extract data reliably using regular expressions or other parsing techniques.

## Switch to OCR  
Due to these limitations, I decided to use Optical Character Recognition (OCR) with pytesseract. This approach involved converting the PDF pages into high-resolution images and then extracting text using OCR.

The OCR method provided much better results. It successfully captured most of the form’s content and allowed me to extract structured data more reliably. This method also worked effectively on the four scanned attachment files embedded in the PDF.

## Outcome  
OCR helped overcome the challenges faced with parsing the original document using traditional libraries. It allowed for cleaner extraction, especially for image-based or scanned sections.
