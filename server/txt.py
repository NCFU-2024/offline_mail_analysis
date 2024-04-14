import os
import re
import shutil
from email import policy
from email.parser import BytesParser

# Настройки папок
email_folder = 'small'
leaks_folder = 'leaks'
summary_file = 'leaks_summary.txt'

if not os.path.exists(leaks_folder):
    os.makedirs(leaks_folder)

# Регулярные выражения для поиска утечек
leak_patterns = {
    'passport': r'\b\d{4}[ №]*[N]*\d{6}\b',
    'snils': r'\b\d{3}-\d{3}-\d{3} \d{2}\b',
    'phone': r'\+7[\s\-]?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
    'account': r'\b\d{20}\b',
    'card': r'\b(?:\d{4}[- ]?){3}\d{4}\b'
}

total_leaks = 0  # Счетчик утечек

def find_leaks(content):
    leaks_found = {}
    for leak_type, pattern in leak_patterns.items():
        if content:
            matches = re.findall(pattern, content)
            if matches:
                leaks_found[leak_type] = matches
    return leaks_found

def process_email(file_path):
    global total_leaks
    with open(file_path, 'rb') as file:
        msg = BytesParser(policy=policy.default).parse(file)
        content = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == 'text/plain' or ctype == 'text/html':
                    part_content = part.get_payload(decode=True)
                    try:
                        content += part_content.decode('utf-8')
                    except UnicodeDecodeError:
                        content += part_content.decode('utf-8', errors='replace')
        else:
            part_content = msg.get_payload(decode=True)
            if part_content:
                try:
                    content = part_content.decode('utf-8')
                except UnicodeDecodeError:
                    content = part_content.decode('utf-8', errors='replace')

        leaks = find_leaks(content)
        if leaks:
            leak_file_path = os.path.join(leaks_folder, os.path.basename(file_path))
            shutil.copy(file_path, leak_file_path)
            print(f"Leaks detected and file saved: {leak_file_path}")
            total_leaks += 1
        else:
            print(f"No leaks detected in: {os.path.basename(file_path)}")

def scan_emails():
    for filename in os.listdir(email_folder):
        if filename.endswith('.eml'):
            process_email(os.path.join(email_folder, filename))

    # Сохраняем результаты в файл и выводим их
    with open(os.path.join(leaks_folder, summary_file), 'w') as f:
        summary = f"Total unique leaked emails: {total_leaks}"
        f.write(summary)
        print(summary)

if __name__ == "__main__":
    scan_emails()
