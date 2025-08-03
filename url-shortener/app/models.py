# app/models.py

import threading
from datetime import datetime
import random
import string

url_store = {}
lock = threading.Lock()

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def store_url(original_url):
    with lock:
        while True:
            code = generate_short_code()
            if code not in url_store:
                break

        url_store[code] = {
            "url": original_url,
            "clicks": 0,
            "created_at": datetime.utcnow().isoformat()
        }
    return code

def get_url_data(code):
    return url_store.get(code)

def increment_click(code):
    with lock:
        if code in url_store:
            url_store[code]["clicks"] += 1
