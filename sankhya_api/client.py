import os
import json
import logging
import requests

from typing import Optional
from dotenv import load_dotenv
from sankhya_api.utils import limpar_telefone, limpar_cep

# ------------------------------------------------------------------------------
# 🔧 Configurações iniciais
# ------------------------------------------------------------------------------

load_dotenv()

TOKEN = os.getenv("SANKHYA_TOKEN")
APPKEY = os.getenv("SANKHYA_APPKEY")
USERNAME = os.getenv("SANKHYA_USERNAME")
PASSWORD = os.getenv("SANKHYA_PASSWORD")

BASE_URL = "https://api.sankhya.com.br/gateway/v1/mge/service.sbr"
HEADERS_BASE = {
    "Content-Type": "application/json"
}


# ------------------------------------------------------------------------------
# 🔐 Autenticação
# ------------------------------------------------------------------------------

def snk_autenticar_sankhya() -> Optional[str]:
    login_url = "https://api.sankhya.com.br/login"
    headers = {
        "token": TOKEN,
        "appkey": APPKEY,
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
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


# ------------------------------------------------------------------------------
# 🔎 Consulta de código do parceiro pelo CPF
# ------------------------------------------------------------------------------

def snk_buscar_codigo_parceiro(cpf: str) -> Optional[str]:
    token = snk_autenticar_sankhya()
    if not token:
        return None

    url = f"{BASE_URL}?serviceName=CRUDServiceProvider.loadRecords&outputType=json"
    headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

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

    try:
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


# ------------------------------------------------------------------------------
# 📝 Atualização de dados básicos do parceiro
# ------------------------------------------------------------------------------

def snk_atualizar_dados_basicos_parceiro(codparc: str, nomeparc: str, telefone: str, cep: str) -> bool:
    token = snk_autenticar_sankhya()
    if not token:
        logging.error("Não foi possível obter o token de autenticação.")
        return False

    if not codparc:
        logging.error("O código do parceiro (codparc) é obrigatório.")
        return False

    url = f"{BASE_URL}?serviceName=DatasetSP.save&outputType=json"
    headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

    payload = {
        "serviceName": "DatasetSP.save",
        "requestBody": {
            "entityName": "Parceiro",
            "fields": [
                "CODPARC",
                "NOMEPARC",
                "RAZAOSOCIAL",
                "TELEFONE",
                "CEP",
                "TIPPESSOA",
                "CLIENTE",
                "COMPLEMENTO"
            ],
            "records": [
                {
                    "pk": {"CODPARC": codparc},
                    "values": {
                        "1": nomeparc,
                        "2": nomeparc,
                        "3": limpar_telefone(telefone),
                        "4": limpar_cep(cep),
                        "5": "F",
                        "6": "S"
                    }
                }
            ]
        }
    }

    logging.debug("📤 Payload enviado:")
    logging.debug(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        resp_json = response.json()

        logging.debug("📥 Resposta da API:")
        logging.debug(json.dumps(resp_json, indent=2, ensure_ascii=False))

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
