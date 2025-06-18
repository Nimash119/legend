
from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'

DB_NAME = 'database.db'

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                content TEXT
            )
        ''')

@app.route('/')
def index():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT username, content FROM reviews ORDER BY id DESC")
        reviews = c.fetchall()
    return render_template('index.html', reviews=reviews)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            try:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
                conn.commit()
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                return "Пользователь уже существует!"
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = c.fetchone()
            if user:
                session['username'] = username
                return redirect(url_for('index'))
            else:
                return "Неверный логин или пароль"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/add_review', methods=['POST'])
def add_review():
    if 'username' not in session:
        return redirect(url_for('login'))
    content = request.form['content']
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("INSERT INTO reviews (username, content) VALUES (?, ?)", (session['username'], content))
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
