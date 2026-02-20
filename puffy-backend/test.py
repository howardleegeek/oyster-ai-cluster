from app.ext_service import *

if __name__ == '__main__':
    service = TgService("7880110295:AAHd7ZAKTd7MgDiWGzjibOvYZpPY7Ve31jY", "chat_id")
    result = service.check_auth(
        TgOauth("7468227219", "f8f968a1ef36a20df7686750f44b000d7d6d687128b891d3433f322ab2ff2404", 1734567604, "Min"))
    print(result)