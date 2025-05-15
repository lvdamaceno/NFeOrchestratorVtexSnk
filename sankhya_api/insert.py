import json
import logging

from sankhya_api.auth import SankhyaClient
from sankhya_api.fetch import snk_fetch_codigo_parceiro
from sankhya_api.update import snk_atualizar_dados_basicos_parceiro, snk_atualizar_dados_entrega_parceiro
from vtex_api.builders import vtex_order_payload_data


# ------------------------------------------------------------------------------
# 🔎 Cadastro e atualização de parceiro
# ------------------------------------------------------------------------------

def snk_cadastra_atualiza_parceiro(vtex_dict: dict, client: SankhyaClient):
    cpf = vtex_dict.get("CGC_CPF")
    if not cpf:
        logging.error("❌ CPF não informado no dicionário VTEX.")
        return

    codparc = snk_fetch_codigo_parceiro(cpf, client)

    if codparc:
        print('entrando na atualizacao')
        atualizacoes = {
            "atualizacao de dados básicos": snk_atualizar_dados_basicos_parceiro(codparc, vtex_dict, client),
            "atualizacao de endereço de entrega": snk_atualizar_dados_entrega_parceiro(codparc, vtex_dict, client)
        }

        for descricao, sucesso in atualizacoes.items():
            if sucesso:
                logging.info(f"🎉 {descricao.capitalize()} atualizado com sucesso.")
            else:
                logging.error(f"❌ Falha ao atualizar {descricao}.")
    else:
        print('entrando na inclusao')


def snk_cadastra_pedido_snk(vtex_order_id: str, client: SankhyaClient):
    logging.debug('🚀 Iniciando cadastro de novo pedido')
    order_data = vtex_order_payload_data(vtex_order_id)

    nota = {
        "cabecalho": {
            "NUNOTA": {"$": ""},
            "NUMNOTA": {"$": ""},
            "AD_NUNOTAORIG": {"$": f"{order_data['AD_NUNOTAORIG']}"},
            "SERIENOTA": {"$": ""},
            "CODPARC": {"$": f"{order_data['CODPARC']}"},
            "DTNEG": {"$": f"{order_data['DTNEG']}"},
            "CODTIPOPER": {"$": "1001"},
            "CODTIPVENDA": {"$": f"{order_data['CODTIPVENDA']}"},
            "CODVEND": {"$": f"{order_data['CODVEND']}"},
            "CODEMP": {"$": "7"},
            "TIPMOV": {"$": "P"},
            "CODNAT": {"$": "1010100"},
            "AD_ENTREGA": {"$": "S"},
            "CIF_FOB": {"$": "C"}
        },
        "itens": {
            "INFORMARPRECO": True,
            "item": [
                {
                    "NUNOTA": {"$": ""},
                    "CODPROD": {"$": f"{order_data['CODPROD']}"},
                    "QTDNEG": {"$":  f"{order_data['QTDNEG']}"},
                    "CODLOCALORIG": {"$": f"{order_data['CODLOCALORIG']}"},
                    "CODVOL": {"$": "UN"},
                    "AD_MONTAGEM": {"$": "S"},
                    "AD_ENTREGAR": {"$": "S"},
                    "AD_EMPRESASAIDA": {"$": "7"},
                    "VLRUNIT": {"$": f"{order_data['VLRUNIT']}"},
                    "VLRTOT": {"$": f"{order_data['VLRTOT']}"},
                    "PERCDESC": {"$": "0"}
                }
            ]
        }
    }

    payload = {
        "serviceName": "CACSP.incluirNota",
        "requestBody": {
            "nota": nota
        }
    }
    logging.debug(f"📤 Payload para criação do pedido no Sankhya")
    logging.debug(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        logging.info("🔎 Enviando Pedido ao Sankhya…")
        resp = client.get(payload)  # Sankhya exige GET com body para este serviço
        logging.debug("🔍 Resposta completa da API Sankhya:\n" +
                      json.dumps(resp, indent=2, ensure_ascii=False))
        status = resp.get("status")
        msg = resp.get("statusMessage", "")

        if status == "0" or (status == "1" and not msg):
            logging.info("✅ Nota fiscal incluída com sucesso.")
        else:
            logging.error(f"❌ Falha ao incluir nota: status={status} | msg={msg or 'sem mensagem'}")
        return resp
    except Exception as e:
        logging.error(f"🚨 Erro ao chamar CACSP.incluirNota: {e}")
        return {"error": str(e)}
