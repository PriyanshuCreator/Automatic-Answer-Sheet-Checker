import os
import pytesseract
from PIL import Image
import PyPDF2
from docx import Document

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extractText()
    return text

def extract_text_from_image(file_path):
    text = pytesseract.image_to_string(Image.open(file_path))
    return text

def extract_text_from_word(file_path):
    doc = Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + '\n'
    return text

def extract_text_from_file(file_path):
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif file_ext in ('.jpg', '.jpeg', '.png', '.gif'):
        return extract_text_from_image(file_path)
    elif file_ext == '.docx':
        return extract_text_from_word(file_path)
    else:
        return "Unsupported file format"

if __name__ == "__main__":
    file_path = r"C:\Users\DELL\Desktop\Dynasty International School.docx"
    if os.path.exists(file_path):
        text = extract_text_from_file(file_path)
        print("Extracted Text:")
        print(text)
        
        # Split the text into separate items based on the newlines and append them to a list
        extracted_texts = text.split('\n')
        print("Extracted Text List:")
        print(extracted_texts[0])
        
        # Save the extracted text to a new file
        output_file_path = r"C:\Users\DELL\Desktop\question.txt"
        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            output_file.write(text)
            
        print("Extracted text saved to:", output_file_path)
    else:
        print("File not found.")