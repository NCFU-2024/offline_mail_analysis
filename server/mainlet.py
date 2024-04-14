import os
import re
import io
from collections import defaultdict
from email import policy
from email.parser import BytesParser

# Регулярные выражения для поиска данных
patterns = {
    'passport': r'\b\d{4}[ №]*[N]*\d{6}\b',  # Российский номер паспорта
    'snils': r'\b\d{3}-\d{3}-\d{3} \d{2}\b',  # Номер СНИЛС
    'phone': r'\+7[\s\-]?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',  # Российский телефонный номер
    'account': r'\b\d{20}\b',  # Номер счета
    'card': r'\b(?:\d{4}[- ]?){3}\d{4}\b'  # Номер кредитной карты
}

def analyze_emails(directory, output_directory):
    results = defaultdict(int)
    categories_count = defaultdict(int)

    # Проверяем и создаем выходную директорию, если нужно
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    for filename in os.listdir(directory):
        if filename.endswith('.eml'):
            path = os.path.join(directory, filename)
            with open(path, 'rb') as file:
                msg = BytesParser(policy=policy.default).parse(file)
                if 'company.name' in msg['From']:  # Фильтрация по отправителю
                    process_email(msg, results, categories_count, output_directory, filename)

    return results, categories_count

def process_email(msg, results, categories_count, output_directory, filename):
    # Обработка основного тела сообщения
    content = msg.get_body(preferencelist=('plain')).get_content() if msg.get_body(preferencelist=('plain')) else msg.as_string()
    analyze_content(content, results, categories_count, output_directory, filename)

    # Обработка вложений, если они текстовые
    for part in msg.iter_parts():
        if part.get_filename() and part.get_content_type() in ['text/plain', 'text/html']:
            file_data = part.get_payload(decode=True)
            content = file_data.decode(part.get_content_charset('utf-8'))
            analyze_content(content, results, categories_count, output_directory, filename)

def analyze_content(content, results, categories_count, output_directory, filename):
    found_data = {}
    for category, pattern in patterns.items():
        matches = re.findall(pattern, content)
        if matches:
            results[category] += len(matches)
            categories_count['total'] += 1
            if category not in found_data:
                found_data[category] = set(matches)
            else:
                found_data[category].update(matches)
    if found_data:
        save_found_data(found_data, output_directory, filename)

def save_found_data(found_data, output_directory, filename):
    with open(os.path.join(output_directory, filename), 'w') as file:
        for category, data in found_data.items():
            file.write(f"{category.upper()} ({len(data)}): {', '.join(data)}\n")

def report_findings(results, categories_count):
    print("Summary of Data Leaks Found:")
    for category, count in results.items():
        print(f"{category.capitalize()}: {count}")
    print("Total Emails Processed:", categories_count['total'])

# Путь к директории с файлами .eml
test_directory = 'small'
# Путь к директории, в которую будут сохраняться файлы с утечками
output_directory = 'leaks'

results, categories_count = analyze_emails(test_directory, output_directory)
report_findings(results, categories_count)
