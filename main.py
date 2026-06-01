from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os

app = FastAPI()

# Создаём папку для загруженных фото
os.makedirs("static/images", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# === БАЗА ДАННЫХ ===
def init_db():
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()
    
    # Таблица сообщений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, email TEXT, message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблица подписчиков
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE
        )
    ''')
    
    # Таблица схем с поддержкой фото
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patterns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            description TEXT,
            materials TEXT,
            pattern_text TEXT,
            image_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Добавляем схемы с фотографиями
    cursor.execute("SELECT COUNT(*) FROM patterns")
    count = cursor.fetchone()[0]
    
    if count == 0:
        test_patterns = [
            ("Ажурный свитер", "Свитеры", "Средний", 
             "Лёгкий летний свитер с романтичным ажурным узором. Идеален для прохладных летних вечеров.",
             "400 г хлопковой пряжи (100г/300м), спицы №3.5, маркеры для петель",
             "Набрать 180 петель.\nВязать резинкой 2x2 - 4 см.\nПерейти на ажурный узор:\n1 ряд: *2 лиц, накид, 2 вместе лиц*\n2 ряд: все изнаночные\nПовторять 1-2 ряды до высоты 40 см.\nДля пройм закрыть по 8 петель с каждой стороны.\nПлечи: закрыть по 25 петель с каждой стороны.\nГорловина: оставшиеся 40 петель закрыть.",
             "https://i.pinimg.com/736x/aa/11/35/aa11355924230b7a5a418f96b08a2d95.jpg"),
            
            ("Шарф с косами", "Шарфы", "Начинающий",
             "Объёмный тёплый шарф с красивыми косами. Длина 180 см, ширина 25 см.",
             "250 г полушерстяной пряжи (100г/200м), спицы №5, дополнительная спица для кос",
             "Набрать 40 петель.\nКромочные: первую снимать, последнюю вязать изнаночной.\nРаппорт узора (24 петли):\n1-4 ряды: 4 лиц, 4 изн, 8 лиц, 4 изн, 4 лиц\n5 ряд: 4 лиц, 4 изн, 4 петли на доп.спицу за работой, 4 лиц, 4 лиц с доп.спицы, 4 изн, 4 лиц\n6-8 ряды: как 1-4\nПовторять до длины 170 см.\nЗавершить резинкой 2x2 - 10 см.",
             "https://i.pinimg.com/1200x/c7/4d/8f/c74d8fd39627af9381d7bdc027152875.jpg"),
            
            ("Шапка-бини", "Шапки", "Начинающий",
             "Модная шапка-бини двойной вязкой. Подходит на любой размер.",
             "150 г мериносовой пряжи (100г/200м), спицы №4 круговые (40 см), чулочные спицы для убавок",
             "Набрать 100 петель.\nВязать резинкой 1x1 по кругу - 5 см.\nПерейти на лицевую гладь - 15 см.\nУбавки для макушки:\n1 ряд: *8 лиц, 2 вместе лиц* - повторить 10 раз\n2 ряд: все лицевые\n3 ряд: *7 лиц, 2 вместе лиц*\n4 ряд: лицевые\nПродолжать убавки, пока не останется 10 петель.\nСтянуть петли, закрепить нить.",
             "https://i.pinimg.com/736x/8d/02/9b/8d029be5a13f334a664fd2da9c34b2c0.jpg"),
            
            ("Кардиган Лаванда", "Кардиганы", "Сложный",
             "Уютный кардиган регланом сверху с ажурными вставками и рукавами 3/4.",
             "650 г шерстяной пряжи (100г/250м), спицы №4.5 (круговые 80 см), спицы №4 для резинки, 6 пуговиц",
             "Реглан сверху:\nНабрать 120 петель, вязать планку платочной вязкой 3 см.\nРазделить: левая полочка 20, рукав 15, спинка 50, рукав 15, правая полочка 20.\nПрибавки в каждом 2-м ряду до высоты 25 см.\nОтделить рукава, довязать тело до низа 35 см.\nРукава: вязать по кругу 30 см.\nЗавершить резинкой 2x2 - 5 см.",
             "https://i.pinimg.com/736x/8e/b3/c3/8eb3c36f2fb2a7bc845e8cc4d13591fe.jpg"),
            
            ("Тёплые носки", "Носки", "Начинающий",
             "Классические носки с укреплённой пяткой. Размер 37-39.",
             "100 г носочной пряжи (100г/400м), спицы №2.5 (чулочные 5 шт), маркеры",
             "Набрать 64 петли (по 16 на каждую спицу).\nРезинка 2x2 - 5 см.\nВязать лицевой гладью 5 см.\nПятка: вязать на 32 петлях поворотными рядами 5 см.\nУкреплённая пятка: 1 ряд: 1 лиц, 1 снять, повторять\nСтопа: 15-18 см в зависимости от размера.\nМысок: убавки с каждой стороны через ряд.\nОставшиеся 8 петель стянуть.",
             "https://i.pinimg.com/1200x/41/da/5f/41da5f2a7ce5bdedbe7a6f46b14cbed6.jpg")
        ]
        
        for pattern in test_patterns:
            cursor.execute('''
                INSERT INTO patterns (title, category, difficulty, description, materials, pattern_text, image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', pattern)
    
    conn.commit()
    conn.close()

init_db()

# === API ДЛЯ ФОРМЫ ===
@app.post("/api/feedback")
async def save_feedback(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...),
    subscribe: str = Form("off")
):
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)",
        (name, email, message)
    )
    
    if subscribe == "on":
        cursor.execute("INSERT OR IGNORE INTO subscribers (email) VALUES (?)", (email,))
    
    conn.commit()
    conn.close()
    return {"status": "ok"}

# === API ДЛЯ СХЕМ ===
@app.get("/api/patterns")
async def get_all_patterns():
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, category, difficulty, description, image_url FROM patterns ORDER BY id")
    patterns = cursor.fetchall()
    conn.close()
    
    return JSONResponse([{
        "id": p[0], "title": p[1], "category": p[2],
        "difficulty": p[3], "description": p[4], "image_url": p[5]
    } for p in patterns])

@app.get("/api/patterns/{pattern_id}")
async def get_pattern(pattern_id: int):
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patterns WHERE id = ?", (pattern_id,))
    pattern = cursor.fetchone()
    conn.close()
    
    if not pattern:
        raise HTTPException(status_code=404, detail="Схема не найдена")
    
    return JSONResponse({
        "id": pattern[0], "title": pattern[1], "category": pattern[2],
        "difficulty": pattern[3], "description": pattern[4],
        "materials": pattern[5], "pattern_text": pattern[6], "image_url": pattern[7]
    })

# === СТРАНИЦЫ ===
def read_html(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/", response_class=HTMLResponse)
async def home():
    return read_html("index.html")

@app.get("/form.html", response_class=HTMLResponse)
async def form_page():
    return read_html("form.html")

@app.get("/pattern/{pattern_id}", response_class=HTMLResponse)
async def view_pattern(pattern_id: int):
    return read_html("pattern_view.html")

@app.get("/admin", response_class=HTMLResponse)
async def admin():
    conn = sqlite3.connect('site.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback ORDER BY id DESC")
    feedbacks = cursor.fetchall()
    cursor.execute("SELECT COUNT(*) FROM subscribers")
    subscribers_count = cursor.fetchone()[0]
    conn.close()
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Админка</title>
    <style>
        body {{ font-family: Arial; padding: 20px; background: #f5ede0; }}
        h1 {{ color: #8b4513; }}
        table {{ width: 100%; border-collapse: collapse; background: white; }}
        th, td {{ padding: 10px; border: 1px solid #deb887; }}
        th {{ background: #8b4513; color: white; }}
    </style>
    </head>
    <body>
        <h1>📋 Админ-панель</h1>
        <p>📧 Подписчиков: {subscribers_count}</p>
        <h2>📝 Сообщения</h2>
        <table><th>ID</th><th>Имя</th><th>Email</th><th>Сообщение</th><th>Дата</th></tr>
    """
    for row in feedbacks:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3][:100]}</td><td>{row[4]}</td></tr>"
    html += "</table></body></html>"
    return HTMLResponse(html)