import os, random, datetime, re, urllib.request, urllib.parse, json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
user_games = {}
user_memory = {}
JOKES = ["Почему программисты путают Хэллоуин и Рождество? OCT 31 == DEC 25 😂","Колобок укатился к успеху! 🔥","Почему Кызылорда лучшая? Потому что там живешь ты! 😎"]
MOTIVATION = ["Брат, ты уже сделал бота — это 99% не могут! Ты красавчик! 🔥","Сегодня бот, завтра — бизнес! Алга! 💪","Ты из Кызылорды — у тебя характер победителя!"]
FACTS = ["Казахстан — 9-я страна в мире! 🇰🇿","Кызылорда раньше называлась Ак-Мечеть!","Твой мозг быстрее суперкомпьютера!"]
QUIZ = [("Столица Казахстана?","Астана"),("Сколько будет 5*5?","25"),("Город — сердце Сырдарьи?","Кызылорда"),("Как по-казахски 'спасибо'?","Рахмет")]
def ai_answer(question, user_id, name):
    try:
        history = user_memory.get(user_id, [])[-4:]
        context = " ".join(history)
        prompt = f"Ты - Mysik Bot, самый умный, веселый друг из Кызылорды. Говоришь на русском, называешь пользователя 'брат'. Отвечаешь коротко, по-братски, с юмором. История: {context}. {name} спрашивает: {question}. Ответь как лучший друг:"
        url = "https://text.pollinations.ai/" + urllib.parse.quote(prompt)
        req = urllib.request.Request(url, headers={"User-Agent":"Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            ans = r.read().decode().strip()
        if user_id not in user_memory: user_memory[user_id]=[]
        user_memory[user_id].append(f"{question} | {ans[:100]}")
        return ans[:1500] if ans else "Брат, спроси еще раз! 😅"
    except:
        return "Брат, ИИ чуть устал... Попробуй еще раз! 🔥"
def get_weather(text):
    try:
        cities={"кызылорда":(44.85,65.50,"Кызылорда"),"алматы":(43.22,76.88,"Алматы"),"астана":(51.16,71.47,"Астана"),"шымкент":(42.32,69.59,"Шымкент"),"тараз":(42.90,71.36,"Тараз")}
        lat,lon,city=44.85,65.50,"Кызылорда"
        for k,v in cities.items():
            if k in text: lat,lon,city=v
        url=f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code&timezone=Asia%2FAlmaty"
        with urllib.request.urlopen(url,timeout=10) as r: cur=json.loads(r.read().decode())["current"]
        codes={0:"Ясно ☀️",1:"Почти ясно 🌤️",2:"Переменная ⛅",3:"Пасмурно ☁️",45:"Туман 🌫️",51:"Морось 🌧️",61:"Дождь 🌧️",71:"Снег ❄️",95:"Гроза ⛈️"}
        desc=codes.get(cur["weather_code"],"Погода есть 😅")
        t=cur["temperature_2m"]
        advice="Жара! Пей воду 🧢" if t>30 else "Тепло 👕" if t>20 else "Прохладно, куртку! 🧥" if t>10 else "Холодно! Одевайся тепло! 🧥" if t>0 else "Мороз! Шапка! 🥶"
        return f"🌤️ Погода в {city}:\n\n{desc}\n🌡️ {t}°C (ощущается {cur['apparent_temperature']}°C)\n💧 Влажность {cur['relative_humidity_2m']}%\n💨 Ветер {cur['wind_speed_10m']} км/ч\n\nСовет: {advice}"
    except: return "Не смог узнать погоду, попробуй еще раз! 😅"
def get_currency():
    try:
        url="https://api.exchangerate-api.com/v4/latest/KZT"
        with urllib.request.urlopen(url,timeout=10) as r: d=json.loads(r.read().decode())["rates"]
        return f"💵 Курс:\n\n💲 1$ = {1/d['USD']:.0f} тг\n💶 1€ = {1/d['EUR']:.0f} тг\n🇷🇺 1₽ = {1/d['RUB']:.1f} тг"
    except: return "Не смог узнать курс, попробуй позже!"
def smart(text, name, user_id):
    t=text.lower().strip()
    if "погод" in t or "ауа" in t: return get_weather(t)
    if "курс" in t or "доллар" in t: return get_currency()
    if "помощь" in t or "что умеешь" in t or "меню" in t:
        return "🔥 MYSIK BOT — УЛЬТРА 10X 🔥\n\n🤖 Напиши ЛЮБОЙ вопрос — отвечу как ChatGPT!\n🌤️ 'погода' — погода\n💵 'курс' — курс валют\n🎮 'игра' — игры\n😂 'шутка' / 💪 'мотивация' / 🧠 'факт'"
    if "игра" in t: return "🎮 Выбирай!\n\n🔢 'угадай' — загадаю число\n✊ 'камень' / 'ножницы' / 'бумага'\n🧠 'викторина' — проверю ум!"
    if "угадай" in t:
        user_games[user_id]={"game":"guess","num":random.randint(1,10)}
        return "Загадал число от 1 до 10! 🔢 Угадай!"
    if user_id in user_games and user_games[user_id].get("game")=="guess" and t.isdigit():
        num=user_games[user_id]["num"]; g=int(t)
        if g==num:
            del user_games[user_id]; return "КРАСАВЧИК! 🔥🔥🔥 Ты угадал!"
        return "Бери выше! ⬆️" if g<num else "Бери ниже! ⬇️"
    if t in ["камень","ножницы","бумага"]:
        bot=random.choice(["камень","ножницы","бумага"]); win={"камень":"ножницы","ножницы":"бумага","бумага":"камень"}
        res="Ничья! 🤝" if bot==t else "Ты победил! 🏆🔥" if win[t]==bot else "Я победил! 😎 Реванш?"
        return f"Ты: {t}\nЯ: {bot}\n\n{res}"
    if "викторина" in t:
        q,a=random.choice(QUIZ); user_games[user_id]={"game":"quiz","ans":a.lower()}
        return f"🧠 ВИКТОРИНА!\n\nВопрос: {q}"
    if user_id in user_games and user_games[user_id].get("game")=="quiz":
        if t==user_games[user_id]["ans"]:
            del user_games[user_id]; return "Правильно! Ты гений! 🧠🔥 Еще? 'викторина'"
        ans=user_games[user_id]["ans"]; del user_games[user_id]
        return f"Мимо... Правильно: {ans}. Давай еще — 'викторина'!"
    if "шутка" in t: return random.choice(JOKES)
    if "мотивац" in t or "лень" in t or "устал" in t: return random.choice(MOTIVATION)
    if "факт" in t: return random.choice(FACTS)
    if "время" in t:
        now=datetime.datetime.now()+datetime.timedelta(hours=5); return f"Сейчас: {now.strftime('%H:%M')} 🕐 Кызылорда"
    m=re.search(r'(\d+)\s*([\+\-\*/])\s*(\d+)',t)
    if "сколько" in t and m:
        a,op,b=int(m.group(1)),m.group(2),int(m.group(3)); res=a+b if op=='+' else a-b if op=='-' else a*b if op=='*' else a/b if b!=0 else "нельзя!"
        return f"{a} {op} {b} = {res} 🧮"
    if "спасибо" in t or "рахмет" in t: return "Всегда пожалуйста, брат! 😎"
    if "пока" in t: return "Пока, брат! 👋"
    return ai_answer(text, user_id, name)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    n=update.effective_user.first_name
    await update.message.reply_text(f"Салам, {n}! 🔥🔥🔥\n\nЯ MYSIK BOT — в 10 РАЗ УМНЕЕ! 🧠 x10\n\nУ меня теперь настоящий ИИ!\nСпроси меня ЧТО УГОДНО!\n\nПримеры:\n🤖 'Кто такой Абай?'\n✍️ 'Напиши пост про Кызылорду'\n🌤️ 'Погода'\n💵 'Курс'")
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Думаю... 🧠💭")
    ans=smart(update.message.text, update.effective_user.first_name, update.effective_user.id)
    await update.message.reply_text(ans)
if __name__=="__main__":
    token=os.environ.get("BOT_TOKEN")
    app=ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    print("ULTRA 10X Bot started...")
    app.run_polling()
