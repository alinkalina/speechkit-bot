import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from speechkit import text_to_speech, speech_to_text
from database import add_user, start_tts_text, set_voice, get_voice, set_text, start_stt_text, set_blocks
from check_limits import check_tts_limits, check_stt_limits
from limits import MAX_SYMBOLS_IN_MESSAGE, MAX_SYMBOLS_FOR_USER, MAX_BLOCKS_FOR_USER, MAX_BLOCKS_IN_MESSAGE, SECONDS_IN_BLOCK
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
    symbols = check_tts_limits(user_id)[1]
    if MAX_SYMBOLS_FOR_USER - symbols >= MAX_SYMBOLS_IN_MESSAGE:
        return MAX_SYMBOLS_IN_MESSAGE
    return MAX_SYMBOLS_FOR_USER - symbols


def available_blocks(user_id):
    blocks = check_stt_limits(user_id)[1]
    if MAX_BLOCKS_FOR_USER - blocks >= MAX_BLOCKS_IN_MESSAGE:
        return MAX_BLOCKS_IN_MESSAGE
    return MAX_BLOCKS_FOR_USER - blocks


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
        if check_tts_limits(message.chat.id)[0]:
            start_tts_text(message.chat.id)
            bot.send_message(message.chat.id, 'Выбери голос', reply_markup=create_markup(list(voices.keys())))
        else:
            bot.send_message(message.chat.id, 'К сожалению, у тебя закончились все символы для синтеза речи',
                             reply_markup=ReplyKeyboardRemove())
    else:
        with open('no_empty.ogg', 'rb') as f:
            bot.send_audio(message.chat.id, f, reply_markup=ReplyKeyboardRemove())
        f.close()


def stt(audio):
    if audio.content_type != 'voice':
        msg = bot.send_message(audio.chat.id, 'Нужно отправить голосовое сообщение!', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, stt)
    elif audio.voice.duration > available_blocks(audio.chat.id) * SECONDS_IN_BLOCK:
        msg = bot.send_message(audio.chat.id, f'Это аудио длиннее {available_blocks(audio.chat.id) * SECONDS_IN_BLOCK} '
                                              f'секунд. Отправь что-нибудь покороче :)',
                               reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, stt)
    else:
        set_blocks(audio.chat.id, audio.voice.duration)
        file_info = bot.get_file(audio.voice.file_id)
        file = bot.download_file(file_info.file_path)
        response = speech_to_text(file)
        if response:
            bot.send_message(audio.chat.id, response, reply_markup=ReplyKeyboardRemove())
        else:
            with open('start_tts.ogg', 'rb') as f:
                bot.send_audio(audio.chat.id, f, reply_markup=ReplyKeyboardRemove())
            f.close()


@bot.message_handler(commands=['stt'])
def stt_command(message):
    if add_user(message.chat.id, message.from_user.username):
        if check_stt_limits(message.chat.id)[0]:
            start_stt_text(message.chat.id)
            msg = bot.send_message(message.chat.id, f'Отправь голосовое сообщение не длиннее '
                                                    f'{available_blocks(message.chat.id) * SECONDS_IN_BLOCK} секунд',
                                   reply_markup=ReplyKeyboardRemove())
            bot.register_next_step_handler(msg, stt)
        else:
            bot.send_message(message.chat.id, 'К сожалению, у тебя закончились все блоки для распознавания речи',
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
