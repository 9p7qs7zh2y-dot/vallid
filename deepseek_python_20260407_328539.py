import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

bot = telebot.TeleBot("8237220454:AAHIs1zJ_h2db7tbPFu7DJWTpp9_PwoLOls")
bot.remove_webhook()

# ========== ПРАВИЛЬНАЯ ССЫЛКА НА ВАШУ ИГРУ ==========
GAME_URL = "https://9p7qs7zh2y-dot.github.io/vallid/"

# Кнопка для игры
game_button = KeyboardButton(
    text="🐨 ТАПАТЬ!",
    web_app=WebAppInfo(url=GAME_URL)
)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = f"""🐨 KOALA × TAP × KOALA

🍃 Привет, {message.from_user.first_name}!

✅ Нажми на кнопку ниже, чтобы начать тапать!"""

    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(game_button)
    
    bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, "📚 Нажми на кнопку ТАПАТЬ, чтобы играть!")

# Когда пользователь пишет любое сообщение
@bot.message_handler(func=lambda message: True)
def handle_other(message):
    response = f"""🍃 Привет, {message.from_user.first_name}!

🌿 Нажми на кнопку ниже, чтобы начать тапать:"""
    
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(game_button)
    
    bot.send_message(message.chat.id, response, reply_markup=keyboard)

if __name__ == "__main__":
    print('✅ Бот запущен!')
    print(f'🎮 Ссылка на игру: {GAME_URL}')
    bot.polling(none_stop=True)