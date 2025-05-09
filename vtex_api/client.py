import requests
from dotenv import load_dotenv
import os
import logging

load_dotenv()


def vtex_fetch_order_data(vtex_order_id):
    # Carregar variáveis do arquivo .env

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
    try:
        logging.info("🔐 Autenticando na API da Vtex...")
        response = requests.get(url, headers=headers)

        # Verificar e imprimir resultado
        if response.status_code == 200:
            logging.debug("Pedido encontrado:")
            return response.json()
        else:
            logging.error(f"Erro: {response.status_code}")
            logging.error(response.text)

    except requests.RequestException as e:
        logging.error(f"Erro ao autenticar: {e}")
        return None


def vtex_fetch_client_data(vtex_order_id):
    dados = vtex_fetch_order_data(vtex_order_id)
    cadastro_cliente = {
        "NOMEPARC": f"{dados['clientProfileData']['firstName']} {dados['clientProfileData']['lastName']}",
        "CGC_CPF": dados['clientProfileData']['document'],
        "TELEFONE": dados['clientProfileData']['phone'],
        "ENDERECO": dados['shippingData']['address']['street'],
        "NUMEND": dados['shippingData']['address']['number'],
        "COMPLEMENTO": dados['shippingData']['address']['complement'],
        "BAIRRO": dados['shippingData']['address']['neighborhood'],
        "CIDADE": dados['shippingData']['address']['city'],
        "CEP": dados['shippingData']['address']['postalCode']
    }
    return cadastro_cliente
