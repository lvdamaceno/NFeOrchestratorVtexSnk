import os
import json
import logging
import requests
from dotenv import load_dotenv
from typing import Any, Dict

# carregar VTEX creds do .env
load_dotenv()

VTEX_ACCOUNT    = os.getenv("VTEX_ACCOUNT")
VTEX_APPKEY     = os.getenv("VTEX_APP_KEY")
VTEX_APPTOKEN   = os.getenv("VTEX_APP_TOKEN")

def vtex_send_invoice(
    order_id: str,
    invoice_data: Dict[str, Any]
) -> Dict[str, Any]:
    if not (VTEX_ACCOUNT and VTEX_APPKEY and VTEX_APPTOKEN):
        raise RuntimeError("VTEX_ACCOUNT, VTEX_APPKEY ou VTEX_APPTOKEN não configurados no .env")

    url = (
        f"https://{VTEX_ACCOUNT}.vtexcommercestable.com.br"
        f"/api/oms/pvt/orders/{order_id}/invoice"
    )
    headers = {
        "X-VTEX-API-AppKey":   VTEX_APPKEY,
        "X-VTEX-API-AppToken": VTEX_APPTOKEN,
        "Accept":              "application/json",
        "Content-Type":        "application/json",
    }

    logging.debug(f"🔗 POST VTEX → {url}")
    logging.debug("📤 Payload:\n%s", json.dumps(invoice_data, indent=2, ensure_ascii=False))

    try:
        resp = requests.post(url, headers=headers, json=invoice_data, timeout=60)
        resp.raise_for_status()
        logging.info(f"✅ Invoice enviada com sucesso para pedido {order_id}")
        return resp.json()
    except requests.RequestException as e:
        logging.error(f"❌ Erro ao enviar invoice para VTEX: {e}")
        return {"error": str(e)}