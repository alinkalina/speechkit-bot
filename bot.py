import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from speechkit import text_to_speech
from database import add_user, start_text, set_voice, get_voice, set_text
from check_limits import check_limits
from limits import MAX_SYMBOLS_IN_MESSAGE, MAX_SYMBOLS_FOR_USER
from config import BOT_TOKEN


bot = telebot.TeleBot(BOT_TOKEN)

voices = {'Мужской': 'filipp', 'Женский': 'jane'}


def create_markup(buttons: list):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(len(buttons)):
        if i % 2 == 0:
            try:
                markup.row(KeyboardButton(buttons[i]), KeyboardButton(buttons[i + 1]))
            except IndexError:
                markup.row(KeyboardButton(buttons[i]))
    return markup


def available_symbols(user_id):
    symbols = check_limits(user_id)[1]
    if MAX_SYMBOLS_FOR_USER - symbols >= MAX_SYMBOLS_IN_MESSAGE:
        return MAX_SYMBOLS_IN_MESSAGE
    return MAX_SYMBOLS_FOR_USER - symbols


@bot.message_handler(commands=['start'])
def send_start_message(message):
    if add_user(message.chat.id, message.from_user.username):
        with open('start_tts.ogg', 'rb') as f:
            bot.send_audio(message.chat.id, f, reply_markup=ReplyKeyboardRemove())
        f.close()
    else:
        with open('no_empty.ogg', 'rb') as f:
            bot.send_audio(message.chat.id, f, reply_markup=ReplyKeyboardRemove())
        f.close()


@bot.message_handler(commands=['tts'])
def tts_command(message):
    if add_user(message.chat.id, message.from_user.username):
        if check_limits(message.chat.id)[0]:
            start_text(message.chat.id)
            bot.send_message(message.chat.id, 'Выбери голос', reply_markup=create_markup(list(voices.keys())))
        else:
            bot.send_message(message.chat.id, 'К сожалению, у тебя закончились все символы для синтеза речи',
                             reply_markup=ReplyKeyboardRemove())
    else:
        with open('no_empty.ogg', 'rb') as f:
            bot.send_audio(message.chat.id, f, reply_markup=ReplyKeyboardRemove())
        f.close()


def tts(text):
    if text.content_type != 'text':
        msg = bot.send_message(text.chat.id, 'Нужно отправить текстовое сообщение!', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, tts)
    elif len(text.text) > available_symbols(text.chat.id):
        msg = bot.send_message(text.chat.id, f'В этом сообщении больше {available_symbols(text.chat.id)} символов. '
                                             f'Отправь что-нибудь покороче :)', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, tts)
    else:
        set_text(text.chat.id, text.text)
        voice = get_voice(text.chat.id)[0][0]
        response = text_to_speech(text.text, voice)
        if response:
            bot.send_audio(text.chat.id, response, reply_markup=ReplyKeyboardRemove())
        else:
            bot.send_message(text.chat.id, 'В SpeechKit произошла ошибка. Попробуй снова чуть позже',
                             reply_markup=ReplyKeyboardRemove())


@bot.message_handler(content_types=['text'])
def text_message(message):
    if message.text in list(voices.keys()):
        set_voice(message.chat.id, voices[message.text])
        msg = bot.send_message(message.chat.id, f'Напиши текст не более {available_symbols(message.chat.id)} символов',
                               reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, tts)
    else:
        bot.send_message(message.chat.id,
                         'Тебе следует воспользоваться командой или кнопкой, другого бот не понимает :(',
                         reply_markup=ReplyKeyboardRemove())


@bot.message_handler(content_types=['photo', 'audio', 'document', 'sticker', 'video', 'voice', 'location', 'contact'])
def error_message(message):
    bot.send_message(message.chat.id, 'Тебе следует воспользоваться командой или кнопкой, другого бот не понимает :(',
                     reply_markup=ReplyKeyboardRemove())


bot.polling()
