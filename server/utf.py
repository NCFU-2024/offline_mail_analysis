import re
import os

# Регулярные выражения для идентификации данных
patterns = {
    'passport': r'\b\d{4}[ №]*[N]*\d{6}\b',
    'snils': r'\b\d{3}-\d{3}-\d{3} \d{2}\b',
    'phone': r'\+7[\s\-]?(?:\(\d{3}\)|\d{3})[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}',
    'account': r'\b\d{20}\b',
    'card': r'\b(?:\d{4}[- ]?){3}\d{4}\b'
}

def search_sensitive_data(file_path):
    results = {key: [] for key in patterns}  # Словарь для хранения результатов
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
        for key, pattern in patterns.items():
            matches = re.findall(pattern, text)
            if matches:
                results[key].extend(matches)
    return results

def save_results(results, output_path):
    with open(output_path, 'w', encoding='utf-8') as file:
        for key, matches in results.items():
            if matches:
                file.write(f"{key}: {matches}\n")

def process_directory(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.txt'):  # Модифицируйте условие для поддержки других типов файлов
            file_path = os.path.join(directory, filename)
            results = search_sensitive_data(file_path)
            output_path = os.path.join(directory, f"{filename}_results.txt")
            save_results(results, output_path)
            print(f"Results saved for {filename}.")

# Укажите путь к вашей директории с файлами
directory_path = 'path_to_your_directory'
process_directory(directory_path)
