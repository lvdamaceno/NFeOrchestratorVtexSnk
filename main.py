from utils import configure_logging
from vtex_api.client import *
from sankhya_api.client import *

if __name__ == '__main__':
    configure_logging()

    # Vtex Order Id
    vtex_order_id = '1530370503117-01'

    # Busca o dados do pedido no Vtex
    dados_cliente = fetch_vtex_client_data(vtex_order_id)
    # Extrai cpf do cliente
    cpf_cliente = dados_cliente['CGC_CPF']

    # Fetch codparc Sankhya Api
    codigo = buscar_codigo_parceiro(cpf_cliente)

    if codigo:
        sucesso = atualizar_dados_basicos_parceiro(codigo, dados_cliente['NOMEPARC'], dados_cliente['TELEFONE'])
        if sucesso:
            print("✅ Cadastro atualizado com sucesso.")
        else:
            print("❌ Falha ao atualizar o cadastro.")
    else:
        print("Criar funcao para cadastro do parceiro")
