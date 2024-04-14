import re
ru = ['а', 'б', 'в', 'г', 'д', 'е', 'ё', 'ж', 'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р', 'с', 'т', 'у', 'ф', 'х',
      'ц', 'ч', 'ш', 'щ', 'ъ', 'ы', 'ь', 'э', 'ю', 'я']

def generate_regex(example):
    regex = r'\b'
    for char in example:
        if char.isalpha():
            if char.isupper() and not (char.lower() in ru):
                regex += '[A-Z]'
            elif char.islower() and not (char.lower() in ru):
                regex += '[a-z]'
            elif char.isupper() and char.lower() in ru:
                regex += '[А-ЯЁ]'
            elif char.islower() and char.lower() in ru:
                regex += '[а-яё]'

        elif char.isdigit():
            regex += '\d'
        elif char.isspace():
            regex += '\s'
        else:
            regex += re.escape(char)
    regex += r'\b'
    return regex


text = input('Введите текст:')
text_regex = generate_regex(text)
print(f"Regex для {text}:", text_regex)
text_pattern = re.compile(text_regex)
print(text_pattern)
text_match = text_pattern.fullmatch("привет")
print("Соответствие шаблону: ", bool(text_match))
