import telebot
from telebot import types
import sqlite3

TOKEN = '7896415232:AAEFT2pLu7U_f9FbLaOn5yw2q96VC-4oYKY'
ADMIN_ID = 456866866  # Замени на свой Telegram ID

bot = telebot.TeleBot(TOKEN)

# Подключение к базе данных
conn = sqlite3.connect('moderation.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS forbidden_words (word TEXT UNIQUE)")
conn.commit()

def get_forbidden_words():
    cursor.execute("SELECT word FROM forbidden_words")
    return {row[0] for row in cursor.fetchall()}

FORBIDDEN_WORDS = get_forbidden_words()

# Главное меню админа
def send_admin_menu(chat_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("⚙ Настройки модерации", callback_data='moderation_settings'))
    markup.add(types.InlineKeyboardButton("🤖 Автоответы", callback_data='auto_replies'))
    markup.add(types.InlineKeyboardButton("📊 Логи", callback_data='logs'))
    markup.add(types.InlineKeyboardButton("👤 Управление пользователями", callback_data='user_management'))
    bot.send_message(chat_id, "<b>🔧 Админ-панель</b>", parse_mode="HTML", reply_markup=markup)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.from_user.id == ADMIN_ID:
        send_admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "Привет! Я бот-модератор. Доступ к админке есть только у администратора.")

# Обработка нажатий на кнопки
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "У вас нет доступа к админ-панели.", show_alert=True)
        return

    if call.data == "moderation_settings":
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("➕ Добавить слово", callback_data='add_word'))
        markup.add(types.InlineKeyboardButton("➖ Удалить слово", callback_data='remove_word'))
        markup.add(types.InlineKeyboardButton("⬅ Назад", callback_data='back_to_admin'))
        bot.send_message(call.message.chat.id, "⚙ Настройки модерации:", reply_markup=markup)
    elif call.data == "add_word":
        bot.send_message(call.message.chat.id, "✏ Введите слово, которое хотите добавить в фильтр (с + в начале):")
    elif call.data == "remove_word":
        bot.send_message(call.message.chat.id, "✏ Введите слово, которое хотите удалить из фильтра (с - в начале):")
    elif call.data == "back_to_admin":
        send_admin_menu(call.message.chat.id)
    elif call.data == "auto_replies":
        bot.send_message(call.message.chat.id, "🤖 Здесь можно будет управлять автоответами.")
    elif call.data == "logs":
        bot.send_message(call.message.chat.id, "📊 Здесь будут отображаться логи.")
    elif call.data == "user_management":
        bot.send_message(call.message.chat.id, "👤 Здесь можно управлять пользователями.")
    bot.answer_callback_query(call.id)

# Фильтрация сообщений
@bot.message_handler(func=lambda message: True)
def message_filter(message):
    global FORBIDDEN_WORDS

    # Админ добавляет или удаляет слова
    if message.from_user.id == ADMIN_ID:
        if message.text.startswith('+'):
            word = message.text[1:].strip().lower()
            cursor.execute("INSERT OR IGNORE INTO forbidden_words (word) VALUES (?)", (word,))
            conn.commit()
            FORBIDDEN_WORDS = get_forbidden_words()
            bot.send_message(message.chat.id, f"✅ Слово '{word}' добавлено в фильтр.")
            return

        elif message.text.startswith('-'):
            word = message.text[1:].strip().lower()
            cursor.execute("DELETE FROM forbidden_words WHERE word = ?", (word,))
            conn.commit()
            FORBIDDEN_WORDS = get_forbidden_words()
            bot.send_message(message.chat.id, f"✅ Слово '{word}' удалено из фильтра.")
            return

    # Проверка обычных сообщений на запрет
    if any(word in message.text.lower() for word in FORBIDDEN_WORDS):
        try:
            bot.delete_message(message.chat.id, message.message_id)
            bot.send_message(message.chat.id, f"🚨 {message.from_user.first_name}, нельзя использовать запрещённые слова!")
        except Exception:
            pass  # Если бот не админ — удаление не сработает

# 🔁 Запуск бота
if __name__ == "__main__":
    print("Бот запущен")
    bot.infinity_polling()
