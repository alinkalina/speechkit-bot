import requests
from config import IAM_TOKEN, FOLDER_ID


def text_to_speech(text, voice):
    headers = {
        'Authorization': f'Bearer {IAM_TOKEN}',
    }
    data = {
        'text': text,
        'lang': 'ru-RU',
        'voice': voice,
        'folderId': FOLDER_ID,
    }

    response = requests.post('https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize', headers=headers, data=data)

    if response.status_code == 200:
        return response.content
    return False
