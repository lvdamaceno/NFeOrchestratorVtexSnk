import json
from datetime import datetime

from dotenv import load_dotenv
import logging

from sankhya_api.auth import SankhyaClient
from sankhya_api.fetch import snk_fetch_codigo_parceiro
from vtex_api.fetch import vtex_fetch_order_data, vtex_fetch_customer_data
from vtex_api.utils import vtex_payment_system

load_dotenv()


def vtex_customer_payload_data(vtex_order_id):
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


def vtex_order_payload_data(vtex_order_id):
    # Criar instância autenticada do cliente
    client = SankhyaClient()

    data = vtex_fetch_order_data(vtex_order_id)
    data_atual = datetime.now().strftime("%d/%m/%Y")

    vtex_dict = vtex_customer_payload_data(vtex_order_id)
    cpf = vtex_dict.get("CGC_CPF")
    codparc = snk_fetch_codigo_parceiro(cpf, client)

    vlrunitcents = data['items'][0]['priceDefinition']['sellingPrices'][0]['value']
    vlrunitreais = vlrunitcents/100
    vlrtotcents = data['value']
    vlrtotreais = vlrtotcents/100

    payment_system = data['paymentData']['transactions'][0]['payments'][0]['paymentSystem']

    codtipvenda = vtex_payment_system(payment_system)

    order_data = {
        "NUNOTA": "",
        "NUMNOTA": "",
        "AD_NUNOTAORIG": data['sequence'],
        "SERIENOTA": "",
        "CODPARC": f"{codparc}",
        "DTNEG": f"{data_atual}",
        "CODTIPOPER": "1174",
        "CODTIPVENDA": f"{codtipvenda}",
        "CODVEND": "68",
        "CODEMP": "7",
        "TIPMOV": "P",
        "CODNAT": "1010100",
        "AD_ENTREGA": "S",
        "CIF_FOB": "C",
        "INFORMARPRECO": "S",
        # Melhorar o codigo para quando o pedido tiver mais de um produto
        "CODPROD": f"{data['itemMetadata']['Items'][0]['RefId']}",
        "QTDNEG": f"{data['items'][0]['quantity']}",
        "CODLOCALORIG": "188",
        "AD_MONTAGEM": "S",
        "AD_ENTREGAR": "S",
        "VLRUNIT": f"{vlrunitreais}",
        "VLRTOT": f"{vlrtotreais}"
        # "PERCDESC": "⚠️ registrar o desconto"
    }
    logging.debug(json.dumps(order_data, indent=2, ensure_ascii=False))
    return order_data
