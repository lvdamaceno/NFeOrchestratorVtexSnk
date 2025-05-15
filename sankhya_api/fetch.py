import json
import logging
from typing import Optional

import requests

from sankhya_api.auth import SankhyaClient

from sankhya_api.utils import extrair_prefixo_sufixo_logradouro, buscar_abreviacoes


ABREVIACOES = {
    "R": "Rua",
    "R.": "Rua",
    "RUA": "Rua",
    "Av": "Avenida",
    "Av.": "Avenida",
    "A": "Avenida",
    "Trav": "Travessa",
    "Trav.": "Travessa",
    "TV.": "Travessa",
    "TV": "Travessa",
    "TVs": "Travessa",
    "TVS": "Travessa",
    "Al": "Alameda",
    "ALA": "Alameda",
    "ALAMEDA": "Alameda",
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
# 🔎 Consulta de código do parceiro pelo CPF
# ------------------------------------------------------------------------------

def snk_fetch_codigo_parceiro(cpf: str, client: SankhyaClient) -> Optional[str]:
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
        logging.info(f"🔎 Consultando parceiro com CPF: {cpf}")
        data = client.get(payload)
        entity = data.get("responseBody", {}).get("entities", {}).get("entity")
        logging.debug(json.dumps(entity, indent=2, ensure_ascii=False))
        if entity and "f1" in entity:
            codigo = entity["f1"]["$"]
            logging.info(f"✅ Parceiro encontrado. Código: {codigo}")
            return codigo
        else:
            logging.warning("⚠️ Parceiro não encontrado.")
            return None

    except requests.RequestException as e:
        logging.error(f"❌ Erro ao buscar parceiro: {e}")
        return None


# ------------------------------------------------------------------------------
# 🔎 Consulta de códigos do endereço com dados vindos do vtex
# ------------------------------------------------------------------------------

def snk_fetch_codend(endereco: str, client: SankhyaClient) -> Optional[str]:
    endereco_prefixo, endereco_sufixo = extrair_prefixo_sufixo_logradouro(endereco)
    abreviacoes_possiveis = buscar_abreviacoes(endereco_prefixo, ABREVIACOES)

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
        data = client.get(payload)
        entity = data.get("responseBody", {}).get("entities", {}).get("entity")
        logging.debug(json.dumps(entity, indent=2, ensure_ascii=False))

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


def snk_fetch_codbai(bairro: str, client: SankhyaClient) -> Optional[str]:
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
        data = client.get(payload)
        entity = data.get("responseBody", {}).get("entities", {}).get("entity")
        logging.debug(json.dumps(entity, indent=2, ensure_ascii=False))

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


def snk_fetch_codcid(cidade: str, client: SankhyaClient) -> Optional[str]:
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
        data = client.get(payload)
        entity = data.get("responseBody", {}).get("entities", {}).get("entity")
        logging.debug(json.dumps(entity, indent=2, ensure_ascii=False))

        if not entity:
            logging.warning("⚠️ Nenhum resultado retornado da API.")
            return None

        # Garante que seja uma lista
        if isinstance(entity, dict):
            entity = [entity]

        codcid = next(
            (item.get('f0', {}).get('$') for item in entity if item.get('f0', {}).get('$')),
            None
        )

        if codcid:
            logging.info(f"✅ CodCid encontrado: {codcid}")
        else:
            logging.warning("⚠️ Nenhum CodCid foi encontrado.")

        return codcid

    except requests.RequestException as e:
        logging.error(f"❌ Erro ao buscar bairro: {e}")
        return None
