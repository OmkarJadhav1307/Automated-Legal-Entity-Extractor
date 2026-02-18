import pytesseract
from pdf2image import convert_from_path
import os

# Linked  Tesseract and Poppler paths 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
POPPLER_PATH = r'C:\poppler\poppler-25.12.0\Library\bin'

def extract_contract_text(pdf_path):
    # Convert PDF to images
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    
    full_text = ""
    for i, image in enumerate(images):
        # Extract text from each image page
        page_text = pytesseract.image_to_string(image)
        full_text += f"\n--- PAGE {i+1} ---\n" + page_text
        
    return full_text

if __name__ == "__main__":
    # Ensure you have a 'data' folder with a 'sample.pdf' in it
    pdf_input = "data/sample.pdf"
    if os.path.exists(pdf_input):
        print("Starting OCR extraction...")
        text = extract_contract_text(pdf_input)
        
        # Save the result to a text file for Annotation
        with open("data/extracted_text.txt", "w") as f:
            f.write(text)
        print("Success! Text saved to data/extracted_text.txt")
    else:
        print(f"Error: Could not find {pdf_input}")