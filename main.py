from utils import configure_logging
from vtex_api.builders import *
from sankhya_api.insert import *

configure_logging()


def processa_cadastro_parceiro_vtex_snk(order_id):
    # Busca o dados do pedido no Vtex
    vtex_dados_cliente = vtex_customer_payload_data(order_id)

    # Cadastra ou atualiza parceiro no sankhya
    snk_cadastra_atualiza_parceiro(vtex_dados_cliente, client)


if __name__ == '__main__':
    # Criar instância autenticada do cliente
    client = SankhyaClient()

    vtex_order_id = '1530370503117-01'
    processa_cadastro_parceiro_vtex_snk(vtex_order_id)

    # Criar pedido no Sankhya
    # snk_cadastra_pedido_snk(vtex_order_id, client)


