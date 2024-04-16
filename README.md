# Бот SpeechKit

[Ссылка](https://github.com/alinkalina/speechkit-bot/tree/tts) на репозиторий

[Ссылка](https://t.me/alulamalula_speechkit_bot) на бота (на сервере он не запущен, но можно посмотреть, как я его оформила :) )


## Описание

В боте при помощи команды /tts синтезируется речь, также пользователь может выбрать женский или мужской голос.

В коде отправляются запросы в API Yandex SpeechKit. Для каждого пользователя ограничено количество символов - 1000. Всего пользователей может быть 10.


## Инструкция по запуску проекта
- Клонируйте репозиторий
- Добавьте необходимые библиотеки Python, зависимости прописаны в файле [requirements.txt](https://github.com/alinkalina/speechkit-bot/blob/tts/requirements.txt)
- Создайте файл `config.py` и поместите в него переменные:
  - `BOT_TOKEN` (str) - Ваш токен Телеграм бота
  - `IAM_TOKEN` (str) - Ваш iam токен для доступа к API Yandex SpeechKit
  - `FOLDER_ID` (str) - Ваш folder id для доступа к API Yandex SpeechKit
- Запустите файл `bot.py`
- Перейдите в бота по [ссылке](https://t.me/alulamalula_speechkit_bot) и нажмите СТАРТ
- Команду /tts можно найти в Меню бота


## Контакты
Для связи с разработчиком можно использовать следующие контакты:

- [Telegram](https://t.me/alulamalula)