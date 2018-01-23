import asyncio
import logging
from time import time
from datetime import datetime
from pprint import pprint

import aiohttp
from pymongo import MongoClient


logger = logging.getLogger()


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

MESSAGE_ICONS = {
    'objeto entregue ao': str(u'\U0001F381'),
    'encaminhado': str(u'\U00002197'),
    'postado': str(u'\U0001F4E6'),
}

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


def pacotes_ativos():
    db = get_db()
    pacotes = db.rastreiobot.find()

    pkgs_to_check = []
    for pacote in pacotes:
        last_status = pacote['stat'][-1].lower()
        if any(status in last_status for status in FINISHED_STATUS):
            continue

        pkgs_to_check.append((pacote['code'], len(pacote['stat'])))

    return ['RQ066584435MY']
    return pkgs_to_check[:10]


def get_situacao_icone(situacao):
    for message in MESSAGE_ICONS:
        if message in situacao:
            return MESSAGE_ICONS[message]

    return ''


def get_data(data, hora):
    return datetime.strptime('{} {}'.format(data, hora), '%d/%m/%Y %H:%M')


def monta_mensagem(evento, primeiro_evento):
    # Data
    primeiro_evento_data = get_data(primeiro_evento['data'],
                                    primeiro_evento['hora'])

    evento_data = get_data(evento['data'], evento['hora'])

    delta = evento_data - primeiro_evento_data

    data = '{:%d/%m/%Y %H:%M}'.format(evento_data)
    if delta.days == 1:
        data += ' (1 dia)'
    elif delta.days > 1:
        data += ' ({} dias)'.format(delta.days)

    # Local
    local = evento['unidade'].get('local', '').title()

    # Situacao
    descricao = evento['descricao'].strip()
    situacao = '<b>{}</b> {}'.format(descricao, get_situacao_icone(descricao))
    if 'endereço indicado' in evento['descricao']:
        situacao = (
            '{situacao}\n'
            '{endereco[numero]} {endereco[logradouro]}\n'
            '{endereco[bairro]}'
        ).format(situacao=situacao, endereco=evento['unidade']['endereco'])

    # Observacao
    try:
        observacao = evento['destino'][0]['local']
    except KeyError:
        observacao = None

    mensagem = (
        'Data: {data}\n'
        'Local: {local}\n'
        'Situação: {situacao}\n'
    ).format(data=data, local=local, situacao=situacao)

    if observacao:
        mensagem += 'Observação: {}\n'.format(observacao)

    return mensagem


async def verifica_pedido(session, code, max_retries=3):
    stats = []
    xml = request_xml(code)
    url = 'http://webservice.correios.com.br/service/rest/rastro/rastroMobile'

    response = await session.post(url, data=xml, headers=CORREIOS_HEADER)
    if not response.status == 200:
        raise Exception()

    data = await response.json()

    if data['objeto'][0]['categoria'].startswith('ERRO'):
        # logger.warning(data['objeto'][0]['categoria'])
        return

    return data['objeto'][0]['evento']


async def atualiza_pacotes(session):
    db = get_db()

    pacotes = pacotes_ativos()
    for pacote, num_stats in pacotes:
        eventos = await verifica_pedido(session, pacote)
        if not eventos:
            continue

        if len(eventos) == num_stats:
            continue

        print(pacote)

        stats = ['{} <b>{}</b>'.format(u'\U0001F4EE', pacote)]
        for evento in reversed(eventos):
            stats.append(monta_mensagem(evento, eventos[-1]))

        db.rastreiobot.update_one(
            {
                'code': pacote.upper()
            },
            {
                '$set': {
                    'stat' : stats,
                    'time' : str(time())
                }
            }
        )


def main():
    start = time()

    loop = asyncio.get_event_loop()
    session = aiohttp.ClientSession(loop=loop)

    loop.run_until_complete(atualiza_pacotes(session))
    loop.close()
    session.close()

    print()
    print('Tempo total: {}s'.format(time() - start))
    print('Total: {}'.format(len(pacotes_ativos())))


if __name__ == '__main__':
    main()
