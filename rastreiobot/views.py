from bottery.message import render

from models import Package


async def welcome(message):
    return render(message, 'welcome.md')


async def add_package(message):
    tracking_code = message.text.split()[0]
    content = {'tracking_code': tracking_code}

    if Package.objects.get(tracking_code=tracking_code):
        return render(message, 'package_already_added.md', content)

    Package(tracking_code=tracking_code, users=[]).save()
    return render(message, 'package_added_successfuly.md', content)
