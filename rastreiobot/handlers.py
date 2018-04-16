from bottery import handlers

from views import add_package, welcome


msghandlers = [
    handlers.message('/start', welcome),
    handlers.regex(r'^[A-Za-z]{2}\d{9}[A-Za-z]{2}$', add_package),
]
