import os
import json
import logging
import requests

from typing import Optional
from dotenv import load_dotenv
from sankhya_api.utils import limpar_telefone, limpar_cep, extrair_prefixo_sufixo_logradouro, buscar_abreviacoes

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

ABREVIACOES = {
    "R": "Rua",
    "R.": "Rua",
    "Av": "Avenida",
    "Av.": "Avenida",
    "Trav": "Travessa",
    "Trav.": "Travessa",
    "TV.": "Travessa",
    "TV": "Travessa",
    "TVs": "Travessa",
    "TVS": "Travessa",
    "Al": "Alameda",
    "Al.": "Alameda",
    "Pç": "Praça",
    "Pç.": "Praça",
    "Rod": "Rodovia",
    "Rod.": "Rodovia",
    "Est": "Estrada",
    "Est.": "Estrada",
    "Jd": "Jardim",
    "Jd.": "Jardim",
    "Vl": "Vila",
    "Vl.": "Vila",
    "Baln": "Balneário",
    "Baln.": "Balneário",
    "Conj": "Conjunto",
    "Conj.": "Conjunto",
    "Res": "Residencial",
    "Res.": "Residencial",
    "Cond": "Condomínio",
    "Cond.": "Condomínio",
    "Pq": "Parque",
    "Pq.": "Parque",
    "St": "Setor",
    "St.": "Setor",
    "Lot": "Loteamento",
    "Lot.": "Loteamento"
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
# 🔎 Cadastro e atualização de parceiro
# ------------------------------------------------------------------------------

def snk_cadastra_atualiza_parceiro(vtex_dict):
    # Fetch codparc Sankhya Api
    codigo = snk_buscar_codigo_parceiro(vtex_dict['CGC_CPF'])

    if codigo:
        sucesso = snk_atualizar_dados_basicos_parceiro(codigo, vtex_dict)
        if sucesso:
            logging.info("✅ Cadastro atualizado com sucesso.")
        else:
            logging.error("❌ Falha ao atualizar o cadastro.")
    else:
        print("Criar funcao para cadastro do parceiro")


# ------------------------------------------------------------------------------
# 🔎 Consulta de códigos do endreço com dados vindos do vtex
# ------------------------------------------------------------------------------

def snk_fetch_codend(endereco) -> Optional[str]:
    token = snk_autenticar_sankhya()
    if not token:
        logging.error("❌ Token não obtido.")
        return None

    endereco_prefixo, endereco_sufixo = extrair_prefixo_sufixo_logradouro(endereco)
    abreviacoes_possiveis = buscar_abreviacoes(endereco_prefixo, ABREVIACOES)

    url = f"{BASE_URL}?serviceName=CRUDServiceProvider.loadRecords&outputType=json"
    headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

    payload = {
        "serviceName": "CRUDServiceProvider.loadRecords",
        "requestBody": {
            "dataSet": {
                "rootEntity": "Endereco",
                "includePresentationFields": "N",
                "offsetPage": "0",
                "criteria": {
                    "expression": {
                        "$": f"NOMEEND = '{endereco_sufixo}'"
                    }
                },
                "entity": {
                    "fieldset": {
                        "list": "CODEND, NOMEEND, TIPO"
                    }
                }
            }
        }
    }

    try:
        logging.info(f"🔎 Consultando endereço: {endereco}")
        response = requests.get(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        entity = data.get("responseBody", {}).get("entities", {}).get("entity")

        if not entity or not isinstance(entity, list):
            logging.warning("⚠️ Nenhum resultado retornado da API.")
            return None

        codend = next(
            (item['f0']['$'] for item in entity if item['f2']['$'] in abreviacoes_possiveis),
            None
        )

        if codend:
            logging.info(f"✅ Codend encontrado: {codend}")
        else:
            logging.warning("⚠️ Nenhum codend compatível com o prefixo foi encontrado.")

        return codend

    except requests.RequestException as e:
        logging.error(f"❌ Erro ao buscar endereço: {e}")
        return None


def snk_fetch_codbai(bairro) -> Optional[str]:
    token = snk_autenticar_sankhya()
    if not token:
        logging.error("❌ Token não obtido.")
        return None

    url = f"{BASE_URL}?serviceName=CRUDServiceProvider.loadRecords&outputType=json"
    headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

    payload = {
        "serviceName": "CRUDServiceProvider.loadRecords",
        "requestBody": {
            "dataSet": {
                "rootEntity": "Bairro",
                "includePresentationFields": "N",
                "offsetPage": "0",
                "criteria": {
                    "expression": {
                        "$": f"NOMEBAI LIKE '{bairro}'"
                    }
                },
                "entity": {
                    "fieldset": {
                        "list": "CODBAI,NOMEBAI"
                    }
                }
            }
        }
    }

    try:
        logging.info(f"🔎 Consultando bairro: {bairro}")
        response = requests.get(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        entity = data.get("responseBody", {}).get("entities", {}).get("entity")

        if not entity:
            logging.warning("⚠️ Nenhum resultado retornado da API.")
            return None

        # Garante que seja uma lista
        if isinstance(entity, dict):
            entity = [entity]

        codbai = next(
            (item.get('f0', {}).get('$') for item in entity if item.get('f0', {}).get('$')),
            None
        )

        if codbai:
            logging.info(f"✅ CodBai encontrado: {codbai}")
        else:
            logging.warning("⚠️ Nenhum CodBai foi encontrado.")

        return codbai

    except requests.RequestException as e:
        logging.error(f"❌ Erro ao buscar bairro: {e}")
        return None


def snk_fetch_codcid(cidade) -> Optional[str]:
    token = snk_autenticar_sankhya()
    if not token:
        logging.error("❌ Token não obtido.")
        return None

    url = f"{BASE_URL}?serviceName=CRUDServiceProvider.loadRecords&outputType=json"
    headers = {**HEADERS_BASE, "Authorization": f"Bearer {token}"}

    payload = {
        "serviceName": "CRUDServiceProvider.loadRecords",
        "requestBody": {
            "dataSet": {
                "rootEntity": "Cidade",
                "includePresentationFields": "N",
                "offsetPage": "0",
                "criteria": {
                    "expression": {
                        "$": f"NOMECID LIKE '{cidade}'"
                    }
                },
                "entity": {
                    "fieldset": {
                        "list": "CODCID,NOMECID"
                    }
                }
            }
        }
    }

    try:
        logging.info(f"🔎 Consultando cidade: {cidade}")
        response = requests.get(url, headers=headers, json=payload)
        response.raise_for_status()

        data = response.json()
        entity = data.get("responseBody", {}).get("entities", {}).get("entity")

        if not entity:
            logging.warning("⚠️ Nenhum resultado retornado da API.")
            return None

        # Garante que seja uma lista
        if isinstance(entity, dict):
            entity = [entity]

        codbai = next(
            (item.get('f0', {}).get('$') for item in entity if item.get('f0', {}).get('$')),
            None
        )

        if codbai:
            logging.info(f"✅ CodCid encontrado: {codbai}")
        else:
            logging.warning("⚠️ Nenhum CodCid foi encontrado.")

        return codbai

    except requests.RequestException as e:
        logging.error(f"❌ Erro ao buscar bairro: {e}")
        return None


# ------------------------------------------------------------------------------
# 📝 Atualização de dados básicos do parceiro
# ------------------------------------------------------------------------------

def snk_atualizar_dados_basicos_parceiro(codparc: str, vtex_dict) -> bool:
    token = snk_autenticar_sankhya()
    nomeparc = vtex_dict['NOMEPARC']
    telefone = vtex_dict['TELEFONE']
    cep = vtex_dict['CEP']
    complemento = vtex_dict['COMPLEMENTO']
    numend = vtex_dict['NUMEND']
    codend = snk_fetch_codend(vtex_dict['ENDERECO'])
    codbai = snk_fetch_codbai(vtex_dict['BAIRRO'])
    codcid = snk_fetch_codcid(vtex_dict['CIDADE'])

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
                "TIPPESSOA",
                "CLIENTE",
                "CEP",
                "COMPLEMENTO",
                "NUMEND",
                "CODEND",
                "CODBAI",
                "CODCID"
            ],
            "records": [
                {
                    "pk": {"CODPARC": codparc},
                    "values": {
                        # dados basicos
                        "1": nomeparc,
                        "2": nomeparc,
                        "3": limpar_telefone(telefone),
                        "4": "F",
                        "5": "S",
                        # dados de entrega
                        "6": limpar_cep(cep),
                        "7": complemento,
                        "8": numend,
                        "9": codend,
                        "10": codbai,
                        "11": codcid
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
            logging.warning(
                f"⚠️ API retornou status diferente de sucesso: {status} | Msg: {status_message or 'sem mensagem'}")
            return False

    except requests.RequestException as e:
        logging.error(f"❌ Erro na requisição: {e}")
        return False
