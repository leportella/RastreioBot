from bottery import handlers

from views import add_package, delete_package, delete_package_info, info, welcome


msghandlers = [
    handlers.message('/start', welcome),
    handlers.message('/info', info),
    handlers.regex(r'^[A-Za-z]{2}\d{9}[A-Za-z]{2}$', add_package),
    handlers.message('/del', delete_package_info),
    handlers.regex(r'/del [A-Za-z]{2}\d{9}[A-Za-z]{2}$', delete_package),
]
