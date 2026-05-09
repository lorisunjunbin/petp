import time
import threading

_lock = threading.Lock()
_cache = {}


def get(key):
    with _lock:
        entry = _cache.get(key)
        if entry is None:
            return None, False
        if entry["expire_at"] is not None and time.time() > entry["expire_at"]:
            del _cache[key]
            return None, False
        return entry["value"], True


def set(key, value, ttl=None):
    with _lock:
        expire_at = (time.time() + ttl) if ttl else None
        _cache[key] = {"value": value, "expire_at": expire_at}
        _evict_expired()


def delete(key):
    with _lock:
        _cache.pop(key, None)


def clear():
    with _lock:
        _cache.clear()


def _evict_expired():
    now = time.time()
    expired = [k for k, v in _cache.items() if v["expire_at"] is not None and now > v["expire_at"]]
    for k in expired:
        del _cache[k]
