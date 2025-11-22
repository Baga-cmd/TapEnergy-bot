import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, ContextTypes, CommandHandler
import json

# Загрузка токена
load_dotenv()
TOKEN = os.getenv("8272440601:AAFyIMTEWnqTxdXD_L1-9jbgYsWgwjKJlKQ")

# Файл для хранения прогресса
SAVE_FILE = "progress.json"

# Проверка файла прогресса
if not os.path.exists(SAVE_FILE):
    with open(SAVE_FILE, "w") as f:
        json.dump({}, f)

# Функции для работы с прогрессом
def load_progress():
    with open(SAVE_FILE, "r") as f:
        return json.load(f)

def save_progress(data):
    with open(SAVE_FILE, "w") as f:
        json.dump(data, f)

def get_user_progress(user_id):
    data = load_progress()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "energy": 0,
            "click_power": 1,
            "auto_income": 0
        }
        save_progress(data)
    return data[str(user_id)]

def update_user_progress(user_id, user_data):
    data = load_progress()
    data[str(user_id)] = user_data
    save_progress(data)

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚡ Клик", callback_data="click")],
        [InlineKeyboardButton("🔧 Улучшить клик (100 ⚡)", callback_data="upgrade")],
        [InlineKeyboardButton("⚙ Автогенератор (500 ⚡)", callback_data="auto")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Добро пожаловать в Tap Energy! Нажимай кнопку, чтобы собирать энергию.", reply_markup=reply_markup)

# Обработка кнопок
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user = get_user_progress(user_id)

    if query.data == "click":
        user["energy"] += user["click_power"]
        text = f"Вы кликнули! +{user['click_power']} ⚡\nЭнергия всего: {user['energy']} ⚡"

    elif query.data == "upgrade":
        if user["energy"] >= 100:
            user["energy"] -= 100
            user["click_power"] += 1
            text = f"Клик улучшен! Сила клика: {user['click_power']}\nЭнергия: {user['energy']} ⚡"
        else:
            text = "Недостаточно энергии для улучшения клика!"

    elif query.data == "auto":
        if user["energy"] >= 500:
            user["energy"] -= 500
            user["auto_income"] += 1
            text = f"Автогенератор куплен! Доход в секунду: {user['auto_income']} ⚡\nЭнергия: {user['energy']} ⚡"
        else:
            text = "Недостаточно энергии для автогенератора!"

    update_user_progress(user_id, user)
    await query.edit_message_text(text=text, reply_markup=query.message.reply_markup)

# Автогенерация энергии каждые 5 секунд
import asyncio
async def auto_income_task(application):
    while True:
        data = load_progress()
        for user_id, user_data in data.items():
            user_data["energy"] += user_data["auto_income"]
        save_progress(data)
        await asyncio.sleep(5)

# Запуск бота
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(button))

# Добавляем фоновую задачу автогенератора
app.job_queue.run_repeating(lambda context: asyncio.create_task(auto_income_task(app)), interval=5)

print("Bot is running...")

app.run_polling()
