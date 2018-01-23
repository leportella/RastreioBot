import asyncio
from time import time
from datetime import datetime
from pprint import pprint

import aiohttp
from pymongo import MongoClient


CORREIOS_USER = ''
CORREIOS_PASSWORD = ''
CORREIOS_TOKEN = ''
CORREIOS_HEADER = {
    'Content-Type': 'application/xml',
    'Accept': 'application/json',
    'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.2.1; LG-P875h Build/JZO34L)'
}


FINISHED_STATUS = (
    'objeto entregue ao',
    'objeto apreendido por órgão de fiscalização',
    'objeto devolvido',
    'objeto roubado',
)


def get_db():
    client = MongoClient()
    return client.rastreiobot


def request_xml(code):
    return (
        '<rastroObjeto>'
        '<usuario>{user}</usuario>'
        '<senha>{password}</senha>'
        '<tipo>L</tipo>'
        '<resultado>T</resultado>'
        '<objetos>{code}</objetos>'
        '<lingua>101</lingua>'
        '<token>{token}</token>'
        '</rastroObjeto>'
    ).format(user=CORREIOS_USER, password=CORREIOS_PASSWORD,
             token=CORREIOS_TOKEN, code=code)


def pedidos_ativos():
    db = get_db()
    packages = db.rastreiobot.find()

    pkgs_to_check = []
    for package in packages:
        last_status = package['stat'][-1].lower()
        if any(status in last_status for status in FINISHED_STATUS):
            continue

        pkgs_to_check.append(package['code'])

    return pkgs_to_check


async def verifica_pedido(session, code, max_retries=3):
    print('verificando pedido: %s' % code)
    stats = []
    xml = request_xml(code)
    url = 'http://webservice.correios.com.br/service/rest/rastro/rastroMobile'

    if max_retries == 0:
        print('max retries limit')
        global timeout
        timeout += 1
        return

    try:
        response = await session.post(url, data=xml, headers=CORREIOS_HEADER)
    except:
        return await verifica_pedido(session, code, max_retries-1)

    data = await response.json()
    evento = data['objeto'][0]['evento']
    pprint(evento)
    return evento


def main():
    start = time()

    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)
    task_list = [verifica_pedido(session, pedido) for pedido in pedidos_ativos()]
    super_task = asyncio.wait(task_list)
    done, _ = loop.run_until_complete(super_task)
    loop.close()
    session.close()

    global timeout
    print()
    print('Tempo total: {}s'.format(time() - start))
    print('Total: {}'.format(len(pedidos_ativos())))
    print('Timeout: {}'.format(timeout))


if __name__ == '__main__':
    main()
