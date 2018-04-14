from bottery import handlers

from views import pong, welcome


msghandlers = [
    handlers.message('ping', pong),
    handlers.message('/start', welcome),
]
