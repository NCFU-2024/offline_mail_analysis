import os
import email
import re
import shutil
from email import policy
from email.parser import BytesParser
import fitz  # PyMuPDF

def is_valid_domain(base_domain, domain):
    return domain.endswith(base_domain) or ('.' + base_domain) in domain

def email_filter(from_address, to_address, base_domain):
    from_domain = from_address.split('@')[-1]
    to_domain = to_address.split('@')[-1]
    # Проверяем, что отправитель относится к базовому домену, а получатель - нет
    return is_valid_domain(base_domain, from_domain) and not is_valid_domain(base_domain, to_domain)

def scan_eml_for_emails(eml_file_path, leaks_folder, patterns, base_domain):
    leaked_emails_count = 0  # Счетчик для подсчета утечек в текущем файле .eml

    # Открываем файл .eml и парсим его содержимое
    with open(eml_file_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)

        # Получаем адреса отправителя и получателя
        from_address = msg['From']
        to_address = msg['To']

        # Применяем фильтр доменов
        if email_filter(email.utils.parseaddr(from_address)[1], email.utils.parseaddr(to_address)[1], base_domain):
            # Проходимся по вложениям письма
            for part in msg.iter_attachments():
                # Проверяем, является ли вложение PDF-файлом
                if part.get_content_type() == 'application/pdf':
                    # Получаем содержимое вложения в виде байтов
                    attachment_bytes = part.get_payload(decode=True)

                    # Сканируем PDF-файл на наличие данных по паттернам
                    if scan_pdf_for_patterns(attachment_bytes, patterns):
                        # Если найдены данные, считаем письмо "слитым" и сохраняем его
                        leaked_emails_count += 1
                        save_eml(msg, eml_file_path, leaks_folder)
                        break  # Прерываем цикл, так как уже найдено одно "слитое" письмо

            # Если вложений с PDF не найдено, проверяем само письмо на наличие данных по паттернам
            if not leaked_emails_count:
                body = msg.get_body(preferencelist=('plain', 'html'))
                text = body.get_content()

                # Сканируем текст письма на наличие данных по паттернам
                if scan_text_for_patterns(text, patterns):
                    # Если найдены данные, считаем письмо "слитым" и сохраняем его
                    leaked_emails_count += 1
                    save_eml(msg, eml_file_path, leaks_folder)

    return leaked_emails_count

def scan_pdf_for_patterns(pdf_bytes, patterns):
    # Открываем PDF-файл из байтов
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    # Проходимся по всем страницам PDF
    for page_number in range(pdf_document.page_count):
        page = pdf_document.load_page(page_number)
        text = page.get_text()

        # Проверяем текст страницы на наличие данных по паттернам
        if scan_text_for_patterns(text, patterns):
            # Если найдены данные, считаем письмо "слитым" и завершаем цикл
            pdf_document.close()
            return True

    # Закрываем PDF-файл после сканирования
    pdf_document.close()
    return False

def scan_text_for_patterns(text, patterns):
    for pattern_name, pattern_regex in patterns.items():
        if re.search(pattern_regex, text):
            return True
    return False

def save_eml(msg, eml_file_path, leaks_folder):
    # Формируем имя файла без указания папки "leaks"
    eml_file_name = os.path.basename(eml_file_path)
    # Копируем файл .eml в папку "leaks"
    shutil.copyfile(eml_file_path, os.path.join(leaks_folder, eml_file_name))
    # Suppressing individual save outputs

# Словарь паттернов для анализа
patterns = {
    'passport': r'\b\d{4}[ №]*[N]*\d{6}\b',
    'snils': r'\b\d{3}-\d{3}-\d{3} \d{2}\b',
    'phone': r'\+7[\s\-]?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
    'account': r'\b\d{20}\b',
    'card': r'\b(?:\d{4}[- ]?){3}\d{4}\b'
}

# Путь к папке с .eml файлами и папке для сохранения "слившихся" писем
eml_folder = 'small'
leaks_folder = 'leaks'
base_domain = 'company.name'  # Задаем базовый домен для фильтрации

if not os.path.exists(leaks_folder):
    os.makedirs(leaks_folder)

total_leaked_emails_count = 0  # Общий счетчик "слившихся" писем

# Проходим по всем файлам в папке с .eml файлами
for file_name in os.listdir(eml_folder):
    file_path = os.path.join(eml_folder, file_name)
    if file_path.endswith('.eml'):
        # Передаем base_domain как аргумент функции
        leaked_emails_count = scan_eml_for_emails(file_path, leaks_folder, patterns, base_domain)
        total_leaked_emails_count += leaked_emails_count

# Вывод только окончательной суммы
print(f'Total Emails Processed: {total_leaked_emails_count}')
