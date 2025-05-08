import requests
from dotenv import load_dotenv
import os
import logging

load_dotenv()


def fetch_vtex_order_data(vtex_order_id):
    # Carregar variáveis do arquivo .env
    load_dotenv()

    # Parâmetros da VTEX
    app_key = os.getenv("VTEX_APP_KEY")
    app_token = os.getenv("VTEX_APP_TOKEN")
    account = os.getenv("VTEX_ACCOUNT")

    # Construir URL da API
    url = f"https://{account}.myvtex.com/api/oms/pvt/orders/{vtex_order_id}"

    # Cabeçalhos da requisição
    headers = {
        "X-VTEX-API-AppKey": app_key,
        "X-VTEX-API-AppToken": app_token
    }

    # Requisição GET
    response = requests.get(url, headers=headers)

    # Verificar e imprimir resultado
    if response.status_code == 200:
        logging.debug("Pedido encontrado:")
        return response.json()
    else:
        logging.error(f"Erro: {response.status_code}")
        logging.error(response.text)


def fetch_vtex_client_data(vtex_order_id):
    dados = fetch_vtex_order_data(vtex_order_id)
    cadastro_cliente = {
        "nome": dados['clientProfileData']['firstName'],
        "sobrenome": dados['clientProfileData']['lastName'],
        "cpf": dados['clientProfileData']['document'],
        "telefone": dados['clientProfileData']['phone'],
        "endereco": dados['shippingData']['address']['street'],
        "numero": dados['shippingData']['address']['number'],
        "complemento": dados['shippingData']['address']['complement'],
        "bairro": dados['shippingData']['address']['neighborhood'],
        "cidade": dados['shippingData']['address']['state'],
        "cep": dados['shippingData']['address']['postalCode']
    }
    return cadastro_cliente
