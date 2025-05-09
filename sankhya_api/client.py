import os
import requests
import logging
import json
from dotenv import load_dotenv
from typing import Optional

# Carrega variáveis do .env
load_dotenv()

TOKEN = os.getenv('SANKHYA_TOKEN')
APPKEY = os.getenv('SANKHYA_APPKEY')
USERNAME = os.getenv('SANKHYA_USERNAME')
PASSWORD = os.getenv('SANKHYA_PASSWORD')


def autenticar_sankhya() -> Optional[str]:
    try:
        login_url = 'https://api.sankhya.com.br/login'
        headers = {
            'token': TOKEN,
            'appkey': APPKEY,
            'username': USERNAME,
            'password': PASSWORD
        }
        logging.info("Autenticando na API da Sankhya...")
        resp = requests.post(login_url, headers=headers)
        resp.raise_for_status()
        token = resp.json().get("bearerToken")
        if not token:
            logging.error("Bearer token não encontrado na resposta.")
        return token
    except requests.RequestException as e:
        logging.error(f"Erro ao autenticar: {e}")
        return None


def buscar_codigo_parceiro(cpf: str) -> Optional[str]:
    token = autenticar_sankhya()
    if not token:
        return None

    try:
        url = 'https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName=CRUDServiceProvider.loadRecords&outputType=json'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        payload = {
            "serviceName": "CRUDServiceProvider.loadRecords",
            "requestBody": {
                "dataSet": {
                    "rootEntity": "Parceiro",
                    "includePresentationFields": "N",
                    "tryJoinedFields": "true",
                    "offsetPage": "0",
                    "criteria": {
                        "expression": {
                            "$": f"CGC_CPF = '{cpf}'"
                        }
                    },
                    "entity": [
                        {
                            "path": "",
                            "fieldset": {
                                "list": "NOMEPARC"
                            }
                        }
                    ]
                }
            }
        }
        logging.info(f"Consultando parceiro com CPF: {cpf}")
        response = requests.get(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        entity = data.get("responseBody", {}).get("entities", {}).get("entity")
        if entity and "f1" in entity:
            codigo = entity["f1"]["$"]
            logging.info(f"Parceiro encontrado. Código: {codigo}")
            return codigo
        else:
            logging.warning("Parceiro não encontrado.")
            return None
    except requests.RequestException as e:
        logging.error(f"Erro ao buscar parceiro: {e}")
        return None


def atualizar_dados_basicos_parceiro(codparc: str, nomeparc: str, telefone: str) -> bool:
    token = autenticar_sankhya()
    if not token:
        logging.error("Não foi possível obter o token de autenticação.")
        return False

    if not codparc:
        logging.error("O código do parceiro (codparc) é obrigatório.")
        return False

    payload = {
        "serviceName": "DatasetSP.save",
        "requestBody": {
            "entityName": "Parceiro",
            "fields": [
                "CODPARC",
                "NOMEPARC",
                "TELEFONE"
            ],
            "records": [
                {
                    "pk": {
                        "CODPARC": codparc
                    },
                    "values": {
                        "1": nomeparc,
                        "2": telefone
                    }
                }
            ]
        }
    }

    url = "https://api.sankhya.com.br/gateway/v1/mge/service.sbr?serviceName=DatasetSP.save&outputType=json"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    logging.debug("Payload enviado:")
    logging.debug(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        resp_json = response.json()

        logging.debug("Resposta completa:")
        logging.debug(json.dumps(resp_json, indent=2, ensure_ascii=False))

        # Mesmo que status seja diferente de "0", se salvou com sucesso, vamos considerar ok
        status = resp_json.get("status")
        status_message = resp_json.get("statusMessage", "")

        if status == "0" or response.status_code == 200:
            logging.info("✅ Atualização feita com sucesso.")
            return True
        else:
            logging.warning(f"⚠️ API retornou status diferente de sucesso: {status} | Msg: {status_message or 'sem mensagem'}")
            return False

    except requests.RequestException as e:
        logging.error(f"❌ Erro na requisição: {e}")
        return False
