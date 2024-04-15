from database import get_all_user_texts
from limits import MAX_SYMBOLS_FOR_USER


def check_limits(user_id):
    texts = get_all_user_texts(user_id)
    total_symbols = 0
    for i in texts:
        total_symbols += len(i[0])
    if MAX_SYMBOLS_FOR_USER > total_symbols >= 0:
        return True, total_symbols
    return False, 0
