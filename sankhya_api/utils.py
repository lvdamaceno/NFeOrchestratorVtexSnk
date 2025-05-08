import os
from sankhya_api.request import SankhyaClient

_sankhya_clients = {}


def get_sankhya_client(service):
    if service not in _sankhya_clients:
        base_url = 'https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName='
        endpoint = f"{base_url}{service}&outputType=json"
        _sankhya_clients[service] = SankhyaClient(service, endpoint, 5)
    return _sankhya_clients[service]


def consulta_cpf_sankhya(service, cpf):
    client = get_sankhya_client(service)
    result = client.load_cpf_records(cpf)
    return result


def atualiza_cadastro_parceiro_sankhya():
    pass


def cria_cadastro_parceiro_sankhya():
    print('tem que criar a funcao')
