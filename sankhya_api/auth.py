import logging
import os

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("SANKHYA_TOKEN")
APPKEY = os.getenv("SANKHYA_APPKEY")
USERNAME = os.getenv("SANKHYA_USERNAME")
PASSWORD = os.getenv("SANKHYA_PASSWORD")

# ------------------------------------------------------------------------------
# 🔧 Configurações iniciais
# ------------------------------------------------------------------------------


BASE_URL = "https://api.sankhya.com.br/gateway/v1/mge/service.sbr"
HEADERS_BASE = {
    "Content-Type": "application/json"
}


# ------------------------------------------------------------------------------
# 🔐 Cliente Sankhya com autenticação única
# ------------------------------------------------------------------------------

class SankhyaClient:
    def __init__(self):
        self.token = None
        self.headers = None
        self.base_mge = "https://api.sankhya.com.br/gateway/v1/mge/service.sbr"
        self.base_mgecom = "https://api.sankhya.com.br/gateway/v1/mgecom/service.sbr"
        self._autenticar()

    def _autenticar(self):
        login_url = "https://api.sankhya.com.br/login"
        headers = {
            "token": TOKEN,
            "appkey": APPKEY,
            "username": USERNAME,
            "password": PASSWORD
        }
        try:
            logging.info("🔐 Autenticando na API da Sankhya...")
            resp = requests.post(login_url, headers=headers)
            resp.raise_for_status()
            self.token = resp.json().get("bearerToken")
            if not self.token:
                raise ValueError("Bearer token não encontrado na resposta.")
            self.headers = {**HEADERS_BASE, "Authorization": f"Bearer {self.token}"}
        except requests.RequestException as e:
            logging.error(f"❌ Erro ao autenticar: {e}")
            raise

    def _build_url(self, service_name: str) -> str:
        # detecta serviços de e-commerce (ajuste a condição se tiver mais)
        if service_name.startswith("CACSP."):
            return f"{self.base_mgecom}?serviceName={service_name}&outputType=json"
        else:
            return f"{self.base_mge}?serviceName={service_name}&outputType=json"

    def get(self, payload: dict) -> dict:
        service_name = payload.get("serviceName")
        if not service_name:
            raise ValueError("Payload precisa conter 'serviceName'")
        url = self._build_url(service_name)
        logging.debug(f"🔗 GET Sankhya → {url}")
        resp = requests.get(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()

    def post(self, payload: dict) -> dict:
        service_name = payload.get("serviceName")
        if not service_name:
            raise ValueError("Payload precisa conter 'serviceName'")
        url = self._build_url(service_name)
        logging.debug(f"🔗 POST Sankhya → {url}")
        resp = requests.post(url, headers=self.headers, json=payload)
        resp.raise_for_status()
        return resp.json()
