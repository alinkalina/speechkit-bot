from database import get_all_user_texts, get_user_blocks
from limits import MAX_SYMBOLS_FOR_USER, MAX_BLOCKS_FOR_USER


def check_tts_limits(user_id):
    texts = get_all_user_texts(user_id)
    total_symbols = 0
    for i in texts:
        total_symbols += len(i[0])
    if MAX_SYMBOLS_FOR_USER > total_symbols >= 0:
        return True, total_symbols
    return False, 0


def check_stt_limits(user_id):
    blocks = get_user_blocks(user_id)
    total_blocks = 0
    for i in blocks:
        total_blocks += i[0]
    if MAX_BLOCKS_FOR_USER > total_blocks >= 0:
        return True, total_blocks
    return False, 0
