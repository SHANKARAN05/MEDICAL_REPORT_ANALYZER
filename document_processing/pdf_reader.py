from PyPDF2 import PdfReader

def extract_text_from_pdf(uploaded_file):

    reader = PdfReader(uploaded_file)

    # Handle encrypted PDFs
    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except:
            pass

    text = ""

    for page in reader.pages:
        text += page.extract_text() + "\n"

    return text