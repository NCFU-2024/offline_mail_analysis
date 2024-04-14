import os
import re
import io
from collections import defaultdict
from email import policy
from email.parser import BytesParser
from PyPDF2 import PdfFileReader

# Регулярные выражения для поиска данных
patterns = {
    'passport': r'\b\d{4}[ №]*[N]*\d{6}\b',
    'snils': r'\b\d{3}-\d{3}-\d{3} \d{2}\b',
    'phone': r'\+7[\s\-]?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',  
    'account': r'\b\d{20}\b',                  
    'card': r'\b(?:\d{4}[- ]?){3}\d{4}\b'  
}

def analyze_emails(directory):
    results = defaultdict(int)
    categories_count = defaultdict(int)

    for filename in os.listdir(directory):
        if filename.endswith('.eml'):
            path = os.path.join(directory, filename)
            with open(path, 'rb') as file:
                msg = BytesParser(policy=policy.default).parse(file)
                process_email(msg, results, categories_count)

    return results, categories_count

def process_email(msg, results, categories_count):
    content = msg.get_body(preferencelist=('plain'))
    if content:
        content = content.get_content() if content else msg.as_string()
        print("Processing email content: ", content)  # Логирование содержимого письма
        found_items = {category: bool(re.search(pattern, content)) for category, pattern in patterns.items()}
        for category, found in found_items.items():
            if found:
                results[category] += 1
        if any(found_items.values()):
            categories_count['total'] += 1

    # Обработка всех вложений
    for part in msg.iter_parts():
        content_type = part.get_content_type()
        content = part.get_payload(decode=True)
        text_content = ""
        if content_type == 'text/plain' or content_type == 'text/html':
            text_content = content.decode(part.get_content_charset() if part.get_content_charset() else 'utf-8')
            print("Processing text content: ", text_content)  # Логирование текстового содержимого
        elif content_type == 'application/pdf':
            text_content = extract_text_from_pdf(content)
            print("Processing PDF content: ", text_content)  # Логирование содержимого PDF
        else:
            continue

        for category, pattern in patterns.items():
            if re.search(pattern, text_content):
                results[category] += 1
                categories_count['total'] += 1
                break

def extract_text_from_pdf(pdf_content):
    pdf = PdfFileReader(io.BytesIO(pdf_content))
    text = ""
    for page in range(pdf.numPages):
        text += pdf.getPage(page).extractText()
    return text

# Функция для вывода результатов
def report_findings(results, categories_count):
    print("Summary of Data Leaks Found:")
    for category, count in results.items():
        print(f"{category.capitalize()}: {count}")
    print("Total Emails Found:", categories_count['total'])

# Путь к директории с файлами .eml
test_directory = 'small'
results, categories_count = analyze_emails(test_directory)
report_findings(results, categories_count)
