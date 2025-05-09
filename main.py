from utils import configure_logging
from vtex_api.client import *
from sankhya_api.client import *


def processa_cadastro_parceiro_vtex_snk(order_id):
    # Busca o dados do pedido no Vtex
    vtex_dados_cliente = vtex_fetch_client_data(order_id)

    # Cadastra ou atualiza parceiro no sankhya
    snk_cadastra_atualiza_parceiro(vtex_dados_cliente)


if __name__ == '__main__':
    configure_logging()

    # Vtex Order Id
    vtex_order_id = '1530370503117-01'
    processa_cadastro_parceiro_vtex_snk(vtex_order_id)
