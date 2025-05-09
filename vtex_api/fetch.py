import json
import logging
import os

import requests
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

VTEX_APP_KEY = os.getenv("VTEX_APP_KEY")
VTEX_APP_TOKEN = os.getenv("VTEX_APP_TOKEN")


def vtex_fetch_customer_data(vtex_order_id):
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
            logging.debug(f"Pedido {vtex_order_id} encontrado:")
            logging.debug(json.dumps(response.json(), indent=2, ensure_ascii=False))
            return response.json()
        else:
            logging.error(f"Erro: {response.status_code}")
            logging.error(response.text)

    except requests.RequestException as e:
        logging.error(f"Erro ao autenticar: {e}")
        return None
