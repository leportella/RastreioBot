from decouple import config
from mongoengine import connect

HOSTNAME = 'localhost'

SECRET_KEY = ''

PLATFORMS = {
    'telegram': {
        'ENGINE': 'bottery.platform.telegram',
        'OPTIONS': {
            'token': config('TELEGRAM_TOKEN'),
        }
    },
}

connect('rastreiobot')
