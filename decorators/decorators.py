import asyncio

def reload_log_after(func):
    def wrapper(*args, **kwargs):
        val = func(*args, **kwargs)

        asyncio.run(
            args[0].on_load_log_async()
        )

        return val

    return wrapper
# end of reload_log_after