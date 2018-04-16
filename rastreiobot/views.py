from bottery.message import render

from models import Package

async def welcome(message):
    return render(message, 'welcome.md')

async def add_package(message):
    tracking_code = message.text.split()[0]
    Package(tracking_code=tracking_code, users=[]).save()
    return code
