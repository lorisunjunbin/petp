import asyncio


def reload_log_after(func):
    def wrapper(instance, *args, **kwargs):
        result = func(instance, *args, **kwargs)
        asyncio.run(instance.on_load_log_async())
        return result

    return wrapper
