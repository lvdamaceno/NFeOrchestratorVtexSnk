import json
import logging

from sankhya_api.auth import SankhyaClient
from sankhya_api.fetch import snk_fetch_codigo_parceiro
from sankhya_api.update import snk_atualizar_dados_basicos_parceiro, snk_atualizar_dados_entrega_parceiro
from vtex_api.client import vtex_order_data
from vtex_api.fetch import vtex_fetch_order_data


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
        atualizacoes = {
            "dados básicos": snk_atualizar_dados_basicos_parceiro(codparc, vtex_dict, client),
            "endereço de entrega": snk_atualizar_dados_entrega_parceiro(codparc, vtex_dict, client)
        }

        for descricao, sucesso in atualizacoes.items():
            if sucesso:
                logging.info(f"🎉 {descricao.capitalize()} atualizado com sucesso.")
            else:
                logging.error(f"❌ Falha ao atualizar {descricao}.")
    else:
        logging.info("🆕 Cliente não encontrado. Implementar função de cadastro.")


def snk_cadastra_pedido_snk(vtex_order_id):
    logging.debug('🚀 Iniciando cadastro de novo pedido')
    order_data = vtex_order_data(vtex_order_id)

    # Criar o pedido no Sankhya usando o dicioanario com dados do VTEX
    return order_data
