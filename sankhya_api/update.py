import json
import logging
from datetime import datetime
from typing import Dict

import requests

from notifications.telegram import enviar_notificacao_telegram
from sankhya_api.auth import SankhyaClient
from sankhya_api.fetch import snk_fetch_codend, snk_fetch_codbai, snk_fetch_codcid, snk_fetch_codigo_parceiro
from sankhya_api.utils import limpar_telefone, limpar_cep


# ------------------------------------------------------------------------------
# 📝 Atualização de dados básicos do parceiro
# ------------------------------------------------------------------------------

def snk_atualizar_dados_basicos_parceiro(codparc: str, vtex_dict, client: SankhyaClient) -> bool:
    logging.info("🚀 Iniciando atualização de dados básicos")
    nomeparc = vtex_dict['NOMEPARC']
    telefone = vtex_dict['TELEFONE']
    cep = vtex_dict['CEP']
    complemento = vtex_dict['COMPLEMENTO']
    numend = vtex_dict['NUMEND']
    codend = snk_fetch_codend(vtex_dict['ENDERECO'], client)
    codbai = snk_fetch_codbai(vtex_dict['BAIRRO'], client)
    codcid = snk_fetch_codcid(vtex_dict['CIDADE'], client)

    if not codparc:
        logging.error("O código do parceiro (codparc) é obrigatório.")
        return False

    payload = {
        "serviceName": "DatasetSP.save",
        "requestBody": {
            "entityName": "Parceiro",
            "fields": [
                # dados basicos
                "CODPARC",
                "NOMEPARC",
                "RAZAOSOCIAL",
                "TELEFONE",
                "TIPPESSOA",
                "CLIENTE",
                # dados de entrega
                "CEP",
                "COMPLEMENTO",
                "NUMEND",
                "CODEND",
                "CODBAI",
                "CODCID",
                # fiscal
                "CSTIPIENT",
                "CSTIPISAI",
                "CLASSIFICMS"

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
                        "11": codcid,
                        # fiscal
                        "12": 49,
                        "13": 99,
                        "14": "C"
                    }
                }
            ]
        }
    }

    logging.debug("📤 Payload dos dados básicos de cadastro enviado:")
    logging.debug(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = client.post(payload)

        logging.debug("📥 Resposta da API:")
        logging.debug(json.dumps(response, indent=2, ensure_ascii=False))

        status = response.get("status")
        status_message = response.get("statusMessage", "")

        if status == "0" or (status == "1" and not status_message):
            logging.info("✅ Atualização dos dados básicos bem-sucedida.")
            return True
        else:
            logging.warning(
                f"⚠️ API retornou status diferente de sucesso: {status} | Msg: {status_message or 'sem mensagem'}")
            return False

    except requests.RequestException as e:
        logging.error(f"❌ Erro na requisição: {e}")
        return False


# ------------------------------------------------------------------------------
# 📝 Atualização de dados de endereço de entrega
# ------------------------------------------------------------------------------

def snk_atualizar_dados_entrega_parceiro(codparc: str, vtex_dict, client: SankhyaClient) -> bool:
    logging.info("🚀 Iniciando atualização do endereço de entrega")
    cep = vtex_dict['CEP']
    complemento = vtex_dict['COMPLEMENTO']
    numend = vtex_dict['NUMEND']
    codend = snk_fetch_codend(vtex_dict['ENDERECO'], client)
    codbai = snk_fetch_codbai(vtex_dict['BAIRRO'], client)
    codcid = snk_fetch_codcid(vtex_dict['CIDADE'], client)

    if not codparc:
        logging.error("O código do parceiro (codparc) é obrigatório.")
        return False

    payload = {
        "serviceName": "DatasetSP.save",
        "requestBody": {
            "entityName": "ComplementoParc",
            "fields": [
                "CODPARC",
                "CODENDENTREGA",
                "NUMENTREGA",
                "COMPLENTREGA",
                "CODBAIENTREGA",
                "CODCIDENTREGA",
                "CEPENTREGA",
                "LOGISTICA"

            ],
            "records": [
                {
                    "pk": {"CODPARC": codparc},
                    "values": {
                        # dados basicos
                        "1": codend,
                        "2": numend,
                        "3": complemento,
                        "4": codbai,
                        "5": codcid,
                        "6": limpar_cep(cep),
                        "7": complemento
                    }
                }
            ]
        }
    }

    logging.debug("📤 Payload do endereço de entrega enviado:")
    logging.debug(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = client.post(payload)

        logging.debug("📥 Resposta da API:")
        logging.debug(json.dumps(response, indent=2, ensure_ascii=False))

        status = response.get("status")
        status_message = response.get("statusMessage", "")

        if status == "0" or (status == "1" and not status_message):
            logging.debug("✅ Atualização de endereço de entrega bem-sucedida.")
            return True
        else:
            logging.warning(
                f"⚠️ API retornou status diferente de sucesso: {status} | Msg: {status_message or 'sem mensagem'}")
            return False

    except requests.RequestException as e:
        logging.error(f"❌ Erro na requisição: {e}")
        return False


# ------------------------------------------------------------------------------
# 📝 Inclusão de dados básicos do parceiro
# ------------------------------------------------------------------------------

def snk_incluir_dados_basicos_parceiro(cpf: str, vtex_dict, client: SankhyaClient) -> bool:
    logging.info("🚀 Iniciando inclusão de dados básicos")
    nomeparc = vtex_dict['NOMEPARC']
    telefone = vtex_dict['TELEFONE']
    cep = vtex_dict['CEP']
    complemento = vtex_dict['COMPLEMENTO']
    numend = vtex_dict['NUMEND']
    codend = snk_fetch_codend(vtex_dict['ENDERECO'], client)
    codbai = snk_fetch_codbai(vtex_dict['BAIRRO'], client)
    codcid = snk_fetch_codcid(vtex_dict['CIDADE'], client)

    payload = {
        "serviceName": "DatasetSP.save",
        "requestBody": {
            "entityName": "Parceiro",
            "fields": [
                # dados basicos
                "CODPARC",
                "NOMEPARC",
                "RAZAOSOCIAL",
                "TELEFONE",
                "TIPPESSOA",
                "CLIENTE",
                # dados de entrega
                "CEP",
                "COMPLEMENTO",
                "NUMEND",
                "CODEND",
                "CODBAI",
                "CODCID",
                # fiscal
                "CSTIPIENT",
                "CSTIPISAI",
                "CLASSIFICMS",
                "CGC_CPF"

            ],
            "records": [
                {
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
                        "11": codcid,
                        # fiscal
                        "12": 49,
                        "13": 99,
                        "14": "C",
                        "15": cpf
                    }
                }
            ]
        }
    }

    logging.debug("📤 Payload dos dados básicos de cadastro enviado:")
    logging.debug(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = client.post(payload)

        logging.debug("📥 Resposta da API:")
        logging.debug(json.dumps(response, indent=2, ensure_ascii=False))

        status = response.get("status")
        status_message = response.get("statusMessage", "")

        if status == "0" or (status == "1" and not status_message):
            logging.info("✅ Inclusão dos dados básicos bem-sucedida.")
            return True
        else:
            logging.warning(
                f"⚠️ API retornou status diferente de sucesso: {status} | Msg: {status_message or 'sem mensagem'}")
            return False

    except requests.RequestException as e:
        logging.error(f"❌ Erro na requisição: {e}")
        return False


# ------------------------------------------------------------------------------
# 📝 Atualização de dados de endereço de entrega
# ------------------------------------------------------------------------------

def snk_incluir_dados_entrega_parceiro(vtex_dict, client: SankhyaClient) -> bool:
    logging.info("🚀 Iniciando inclusão do endereço de entrega")
    cep = vtex_dict['CEP']
    complemento = vtex_dict['COMPLEMENTO']
    numend = vtex_dict['NUMEND']
    codend = snk_fetch_codend(vtex_dict['ENDERECO'], client)
    codbai = snk_fetch_codbai(vtex_dict['BAIRRO'], client)
    codcid = snk_fetch_codcid(vtex_dict['CIDADE'], client)
    cpf = vtex_dict.get("CGC_CPF")
    codparc = snk_fetch_codigo_parceiro(cpf, client)

    if not codparc:
        logging.error("❌ O código do parceiro (codparc) é obrigatório.")
        return False

    payload = {
        "serviceName": "DatasetSP.save",
        "requestBody": {
            "entityName": "ComplementoParc",
            "fields": [
                "CODPARC",
                "CODENDENTREGA",
                "NUMENTREGA",
                "COMPLENTREGA",
                "CODBAIENTREGA",
                "CODCIDENTREGA",
                "CEPENTREGA",
                "LOGISTICA"

            ],
            "records": [
                {
                    "pk": {"CODPARC": codparc},
                    "values": {
                        # dados basicos
                        "1": codend,
                        "2": numend,
                        "3": complemento,
                        "4": codbai,
                        "5": codcid,
                        "6": limpar_cep(cep),
                        "7": complemento
                    }
                }
            ]
        }
    }

    logging.debug("📤 Payload do endereço de entrega enviado:")
    logging.debug(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = client.post(payload)

        logging.debug("📥 Resposta da API:")
        logging.debug(json.dumps(response, indent=2, ensure_ascii=False))

        status = response.get("status")
        status_message = response.get("statusMessage", "")

        if status == "0" or (status == "1" and not status_message):
            logging.debug("✅ Inclusão de endereço de entrega bem-sucedida.")
            return True
        else:
            logging.warning(
                f"⚠️ API retornou status diferente de sucesso: {status} | Msg: {status_message or 'sem mensagem'}")
            return False

    except requests.RequestException as e:
        logging.error(f"❌ Erro na requisição: {e}")
        return False


def snk_confirmar_nota(nunota: str, client: SankhyaClient) -> Dict:
    logging.debug(f"🚀 Iniciando confirmação de nota fiscal {nunota}")
    payload = {
        "serviceName": "CACSP.confirmarNota",
        "requestBody": {
            "nota": {
                "NUNOTA": { "$": nunota }
            }
        }
    }

    try:
        logging.info("🔎 Enviando confirmação de nota ao Sankhya…")
        resp = client.get(payload)  # GET com corpo JSON, como no curl
        logging.debug("🔍 Resposta completa da API Sankhya:\n" +
                      json.dumps(resp, indent=2, ensure_ascii=False))

        status = resp.get("status")
        msg = resp.get("statusMessage", "")

        if status == "0" or (status == "1" and not msg):
            logging.info(f"✅ Nota {nunota} confirmada com sucesso.")
        else:
            logging.error(f"❌ Falha ao confirmar nota {nunota}: status={status} | msg={msg or 'sem mensagem'}")

        return resp

    except Exception as e:
        logging.error(f"🚨 Erro ao chamar CACSP.confirmarNota: {e}")
        return {"error": str(e)}


def snk_faturar_nota(nunota: int, client: SankhyaClient):
    dt_faturamento = datetime.now().strftime("%d/%m/%Y")

    payload = {
        "serviceName": "SelecaoDocumentoSP.faturar",
        "requestBody": {
            "notas": {
                "codTipOper": 1101,
                "dtFaturamento": dt_faturamento,
                "tipoFaturamento": "FaturamentoDireto",
                "dataValidada": True,
                "notasComMoeda": {},
                "nota": [{"$": nunota}],
                "codLocalDestino": "",
                "faturarTodosItens": True,
                "umaNotaParaCada": "false",
                "ehWizardFaturamento": True,
                "dtFixaVenc": "",
                "ehPedidoWeb": False,
                "nfeDevolucaoViaRecusa": False,
                "serie": 1
            }
        }
    }

    logging.debug("🚀 Payload de faturamento:\n" + json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        logging.info(f"🔎 Faturando nota {nunota}…")
        resp = client.get(payload)
        logging.debug("🔍 Resposta da API Sankhya:\n" +
                      json.dumps(resp, indent=2, ensure_ascii=False))
        nunota = resp["responseBody"]["notas"]["nota"]["$"]
        status = resp.get("status")
        msg = resp.get("statusMessage", "")
        if status == "0" or (status == "1" and not msg):
            logging.info(f"✅ Nota {nunota} faturada com sucesso.")
            enviar_notificacao_telegram("✅ Nota {nunota} faturada com sucesso.")

        else:
            logging.error(f"❌ Falha ao faturar nota {nunota}: status={status} | msg={msg or 'sem mensagem'}")
            enviar_notificacao_telegram(f"❌ Falha ao faturar nota {nunota}: status={status} | msg={msg or 'sem mensagem'}")

        return nunota

    except Exception as e:
        logging.error(f"🚨 Erro ao faturar nota {nunota}: {e}")
        return {"error": str(e)}