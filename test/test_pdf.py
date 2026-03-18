import pdfplumber

with pdfplumber.open("/Users/a0b0fei/Documents/personal_docs/amal/Amal_Babu_-_Staff_Software_Engineer.pdf") as pdf:
    text = ""
    for page in pdf.pages:
        text += page.extract_text()

print(text[:1000])
