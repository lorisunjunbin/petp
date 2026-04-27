
def reload_log_after(func):
    def wrapper(instance, *args, **kwargs):
        result = func(instance, *args, **kwargs)
        instance.on_load_log_async()
        return result

    return wrapper

def reload_http_log_after(func):
    def wrapper(instance, *args, **kwargs):
        result = func(instance, *args, **kwargs)
        instance.p.on_load_log_async()
        return result

    return wrapper
