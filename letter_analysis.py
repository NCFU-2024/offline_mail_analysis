from flask import Flask, render_template, request, redirect, url_for, session
import logging

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Секретный ключ для подписи сессии

# Настройка логгера
logging.basicConfig(filename='app.log', level=logging.INFO)

# Предположим, что у вас есть некоторая база данных пользователей
# Здесь мы создаем простой словарь пользователей для демонстрации
users = {
    'user1': 'pass1',
    'user2': 'password2'
}


vulnerabilities_data = [
    {'id': 1, 'Email': 'Volconon@company.name', 'Type': 'Passport'},
    {'id': 2, 'Email': 'LilAngel@company.name', 'Type': 'Card'},
    {'id': 3, 'Email': 'FoxSela@company.name', 'Type': 'Card'},
    {'id': 4, 'Email': 'Timmu@company.name', 'Type': 'Passport'},
    {'id': 5, 'Email': 'Maccus@vip.company.name', 'Type': 'Card'},
    {'id': 6, 'Email': 'Agent77@our.company.name', 'Type': 'Phone'} ,
   {'id': 1, 'Email': 'Firestar55257@our.company.name', 'Type': 'Passport'},
    {'id': 7, 'Email': 'Mendar@company.name', 'Type': 'Card'},
    {'id': 8, 'Email': 'zrober@cards.company.name', 'Type': 'Card'}
]


@app.route('/')
def index():
    if 'username' in session:
        return render_template('menu.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            logging.info(f'Пользователь {username} вошел в систему')
            return redirect(url_for('index'))
        else:
            return 'Неверное имя пользователя или пароль'
    return render_template('login.html')

@app.route('/logout')
def logout():
    if 'username' in session:
        logging.info(f'Пользователь {session["username"]} вышел из системы')
        session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/vulnerabilities')
def vulnerabilities():
    # Обработка нажатия кнопки "Уязвимости"
    logging.info('Кнопка "Уязвимости" нажата')
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('vulnerabilities.html', vulnerabilities=vulnerabilities_data)


@app.route('/check')
def check():
    # Обработка нажатия кнопки "Проверка"
    logging.info('Кнопка "Проверка" нажата')
    # Ваш код для проверки
    return "Проверка"

if __name__ == '__main__':
    app.run(debug=True)
