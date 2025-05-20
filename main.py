from notifications.telegram import enviar_notificacao_telegram
from sankhya_api.fetch import snk_fetch_invoice_data
from sankhya_api.update import snk_confirmar_nota, snk_faturar_nota
from utils import configure_logging
from vtex_api.builders import *
from sankhya_api.insert import *
from vtex_api.invoice import vtex_send_invoice

configure_logging()


def processa_cadastro_parceiro_vtex_snk(order_id):
    # Busca o dados do pedido no Vtex
    vtex_dados_cliente = vtex_customer_payload_data(order_id)
    # Cadastra ou atualiza parceiro no sankhya
    snk_cadastra_atualiza_parceiro(vtex_dados_cliente, client)


def processa_pedido_fatura_nota(order_id):
    # 1) Atualiza ou cadatra parceiro
    processa_cadastro_parceiro_vtex_snk(order_id)

    # 2) Criar pedido no Sankhya
    pedido = snk_cadastra_pedido_snk(order_id, client)

    # 3) Confirma pedido no Sankhya
    snk_confirmar_nota(pedido, client)

    # 4) Fatura pedido no Sankhya
    nota = snk_faturar_nota(pedido, client)

    # 5) Captura o JSON da invoice
    xml = snk_fetch_invoice_data(nota, client)

    # 6) Pergunta ao usuário se quer enviar para a VTEX
    resposta = input(f"Deseja enviar a invoice da nota {nota} para o pedido {order_id}? (s/n): ").strip().lower()
    if resposta and resposta[0] == "s":
        logging.info("👍 Usuário confirmou envio da invoice para VTEX.")
        resultado = vtex_send_invoice(order_id, xml)
        enviar_notificacao_telegram(f"XML da nota {nota} foi enviado para o pedido {order_id} no VTEX")
        logging.debug("Resposta VTEX:", resultado)
    else:
        logging.info("👎 Envio da invoice para VTEX cancelado pelo usuário.")


if __name__ == '__main__':
    # Criar instância autenticada do cliente
    client = SankhyaClient()
    # Cria pedido, confirma, fatura, envia para o vtex
    vtex_order_id = '1533550503135-01'
    processa_pedido_fatura_nota(vtex_order_id)
