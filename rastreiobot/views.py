from bottery.message import render


async def pong(message):
    return 'pong'

async def welcome(message):
    return render(message, 'welcome.md')
