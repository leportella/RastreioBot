from bottery.message import render

from models import Package


async def welcome(message):
    return render(message, 'welcome.md')


async def add_package(message):
    tracking_code = message.text.split()[0]
    content = {'tracking_code': tracking_code}

    package_added = False
    try:
        package = Package.objects.get(tracking_code=tracking_code)
    except Package.DoesNotExist:
        Package(tracking_code=tracking_code, users=[message.user.id]).save()
        package_added = True
    else:
        if message.user.id not in package.users:
            package.users.append(message.user.id)
            package_added = True

    if package_added:
        return render(message, 'package_added_successfuly.md', content)

    return render(message, 'package_already_added.md', content)


async def info(message):
    return render(message, 'bot_info.md')
