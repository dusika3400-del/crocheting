from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import os

app = FastAPI()

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
            ("Ажурный кардиган", "Свитеры", "Средний",
            "Лёгкий летний кардиган с романтичным ажурным узором. Свободный крой, цельновязаные рукава. Идеален для прохладных летних вечеров.",
            "400 г мериносовой пряжи средней толщины (100г/300м), спицы №3.5 и №4, крючок для обвязки, маркеры, 5 пуговиц (по желанию).",
            "Набрать 180 петель на спицы №3.5. Вязать резинкой 1x1 — 6 см. Перейти на спицы №4 и ажурный узор «Вертикальные волны» (раппорт 12 петель + кромочные).\n1 ряд (лиц): *2 лиц, накид, 1 лиц, накид, 2 вместе лиц с наклоном вправо, 2 вместе лиц с наклоном влево, 2 лиц, 3 изн* повторять до конца.\n2 ряд и все четные: по рисунку (накиды — изнаночными).\n3 ряд: *2 лиц, накид, 2 лиц, накид, 2 вместе лиц влево, 1 лиц, 2 вместе лиц вправо, 2 лиц, 1 изн* повторять.\n5 ряд: *2 лиц, накид, 3 лиц, накид, двойная протяжка (снять 1 лиц, 2 вместе лиц, протянуть через снятую), 4 лиц, 1 изн*.\n7 ряд: как 1-й.\nПовторять ряды 1-8 до высоты 42 см.\nДля пройм закрыть с каждой стороны по 1 разу 5 петель, затем 4 раза по 2 петли в каждом 2-м ряду (осталось ~150 петель).\nВязать прямо еще 18 см. Для плеч закрыть по 30 петель в 2 приема (15+15). Оставшиеся 50 петель горловины закрыть свободно.\nПланки: поднять петли по краям полочек, связать резинкой 1x1 — 3 см, на правой планке сделать 5 отверстий под пуговицы.\nОбвязать горловину и проймы крючком «рачьим шагом».",
            "/static/images/cardigan.jpg"),
            
            ("Летний топ с завязками", "Топы", "Начинающий",
            "Длинный летний топ, который завязывается на груди или шее. Универсальная модель: можно носить как палантин, накидку или топ-бандо. Ширина 35 см, длина 160 см.",
            "200 г хлопковой или льняной пряжи (100г/250м), спицы №3.5, игла для сшивания.",
            "Набрать 60 петель. Вязать платочной вязкой 2 см для нижнего края.\nОсновной узор — «Крупный рис»:\n1 ряд: *1 лиц, 1 изн* повторять.\n2 ряд: над лицевыми — изнаночные, над изнаночными — лицевые.\nЧерез 20 см от начала перейти на «Ажурные дорожки»:\n1 ряд (лиц): *2 вместе лиц вправо, накид* повторять.\n2 ряд: все изнаночные.\n3-4 ряды: лицевая гладь.\nПовторять эти 4 ряда до длины 150 см.\nДля завязок: последние 20 петель с каждой стороны не закрывать, а продолжить вязать платочной вязкой еще 30 см (это и будут завязки). Затем закрыть все петли.\nКрая топа обвязать крючком столбиками без накида, на углах завязок сделать кисточки по желанию.",
            "/static/images/top.jpg"),
            
            ("Летний корсет", "Топы", "Начинающий",
            "Изящный летний корсет на шнуровке, облегающий фигуру. Вяжется снизу вверх, с убавками для талии и грудными вытачками. Застёжка на спинке или шнуровка.",
            "250 г хлопковой пряжи (100г/250м), спицы №3 и №3.5, круговые спицы 40 см, крючок для шнуровки, 2 декоративных кольца для шнурка.",
            "Набрать 140 петель на спицы №3. Вязать резинкой 2x2 — 4 см. Перейти на спицы №3.5 и лицевую гладь.\nЧерез 10 см от резинки начать убавки для талии: по 2 петли с каждой стороны в каждом 6-м ряду (5 раз) → останется 120 петель.\nЧерез 25 см от начала — прибавки для груди: по 1 петле с каждой стороны в каждом 4-м ряду (6 раз) → 132 петли.\nЧерез 38 см от начала разделить вязание на две полочки: по 66 петель.\nДля выреза горловины закрыть с внутреннего края в каждом 2-м ряду: 1 раз 5 петель, 1 раз 3 петли, 3 раза по 2 петли, затем 5 раз по 1 петле.\nПроймы: закрыть с внешнего края 1 раз 4 петли, 1 раз 3 петли, 2 раза по 2 петли.\nПлечи закрыть по 25 петель.\nДля шнуровки: на спинке оставить вертикальную планку из 10 петель, обвязать крючком и сделать 8 пар отверстий.\nСвязать шнурок длиной 120 см крючком или полым шнуром на спицах.",
            "/static/images/corset.jpg"),
            
            ("Свитер с атласной лентой", "Свитера", "Сложный",
            "Элегантный свитер прямого силуэта, в котором атласная лента продевается по вырезу горловины и манжетам. Рукава 3/4, декоративные планки с прорезями для ленты.",
            "600 г мериносовой пряжи средней толщины (100г/200м), спицы №4 и №4.5, атласная лента шириной 1 см — 3 метра, игла для ленты.",
            "Спинка: набрать 110 петель на спицы №4. Резинка 1x1 — 6 см. Перейти на спицы №4.5, вязать лицевой гладью 45 см. Для плеч закрыть по 25 петель, для горловины — 40 петель.\nПеред: вязать аналогично, но через 35 см от резинки начать формировать V-образный вырез: убавлять по 1 петле с каждой стороны в каждом 4-м ряду 12 раз.\nВдоль выреза горловины и манжетов связать планки шириной 2 см с отверстиями: *2 лиц, накид, 2 вместе лиц*.\nРукава: набрать 50 петель, резинка 5 см, затем лицевая гладь. Через 25 см от резинки закрыть все петли.\nСшить детали. Продеть атласную ленту в отверстия планок горловины и манжетов, завязать бантом.",
            "/static/images/sviter.jpg"),
            
            ("Летняя сумка Цветок", "Сумки", "Средний",
            "Яркая летняя сумка-шоппер в форме цветка с шестью лепестками. Вяжется из хлопкового шнура. Ручки-косички длиной 50 см. Дно укреплено пластиковой вставкой.",
            "300 г хлопковой пряжи-шнура (100г/150м), спицы №6 круговые (60 см), крючок №4, пластиковое дно для сумки размером 30х10 см, маркеры.",
            "Дно: набрать 40 петель. Вязать платочной вязкой прямоугольник 30х10 см (примерно 30 рядов).\nОсновная часть (лепестки): поднять петли по краю дна (всего ~100 петель). Вязать по кругу.\n1-й лепесток: отметить 15 петель, вязать поворотными рядами: 1 ряд: все лицевые, 2 ряд: 2 вместе изн, остальные изн, 2 вместе изн — повторять, пока не останется 3 петли, закрыть.\nАналогично связать ещё 5 лепестков (через каждые 15 петель).\nВторой ярус лепестков: поднять петли между лепестками первого яруса, повторить схему.\nОбвязать верхний край крючком «рачьим шагом».\nРучки: связать полым шнуром 2 детали длиной 50 см, пришить к двум противоположным лепесткам.",
            "/static/images/bag.jpg"),
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