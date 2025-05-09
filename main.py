from utils import configure_logging
from vtex_api.client import *
from sankhya_api.client import *


def snk_cadastra_atualiza_parceiro(vtex_dict):
    cpf = vtex_dict['CGC_CPF']

    # Fetch codparc Sankhya Api
    codigo = snk_buscar_codigo_parceiro(cpf)

    if codigo:
        sucesso = snk_atualizar_dados_basicos_parceiro(codigo, vtex_dict['NOMEPARC'], vtex_dict['TELEFONE'], vtex_dict['CEP'])
        if sucesso:
            logging.info("✅ Cadastro atualizado com sucesso.")
        else:
            logging.error("❌ Falha ao atualizar o cadastro.")
    else:
        print("Criar funcao para cadastro do parceiro")


if __name__ == '__main__':
    configure_logging()

    # Vtex Order Id
    vtex_order_id = '1530370503117-01'

    # Busca o dados do pedido no Vtex
    vtex_dados_cliente = vtex_fetch_client_data(vtex_order_id)

    snk_cadastra_atualiza_parceiro(vtex_dados_cliente)
