class BotNotify(Exception):
    def __init__(self, message):
        super().__init__(message)


class BotShutdownError(Exception):
    def __init__(self, message):
        super().__init__(message)


class BotShutdown(Exception):
    def __init__(self, message):
        super().__init__(message)
