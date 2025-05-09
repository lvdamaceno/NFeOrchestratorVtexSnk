import json
from datetime import datetime

import requests
from dotenv import load_dotenv
import os
import logging

from vtex_api.fetch import vtex_fetch_order_data, vtex_fetch_customer_data

load_dotenv()


def vtex_customer_data(vtex_order_id):
    dados = vtex_fetch_customer_data(vtex_order_id)
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


def vtex_order_data(vtex_order_id):
    data = vtex_fetch_order_data(vtex_order_id)
    data_atual = datetime.now().strftime("%d/%m/%Y")
    order_data = {
        "NUNOTA": "",
        "NUMNOTA": "",
        "AD_NUNOTAORIG": data['sequence'],
        "SERIENOTA": "",
        "CODPARC": "⚠️ Usar a funcao de buscar codparc",
        "DTNEG": data_atual,
        "CODTIPOPER": "1174",
        "CODTIPVENDA": "190",
        "CODVEND": "⚠️ Colocar o ecommerce",
        "CODEMP": "7",
        "TIPMOV": "P",
        "CODNAT": "1010100",
        "AD_ENTREGA": "S",
        "CIF_FOB": "C",
        "INFORMARPRECO": "S",
        # Melhorar o codigo para quando o pedido tiver mais de um produto
        "CODPROD": data['itemMetadata']['Items'][0]['RefId'],
        "QTDNEG": data['items'][0]['quantity'],
        "CODLOCALORIG": "188",
        "CODVOL": "⚠️ pegar o volume do cadastro do produto",
        "AD_MONTAGEM": "⚠️ como saber se monta ou nao?",
        "AD_ENTREGAR": "S",
        "VLRUNIT": data['items'][0]['priceDefinition']['sellingPrices'][0]['value'],
        "VLRTOT": data['value'],
        "PERCDESC": "⚠️ registrar o desconto"
    }
    logging.debug(json.dumps(order_data, indent=2, ensure_ascii=False))
    return order_data
