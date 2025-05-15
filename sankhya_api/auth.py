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

    def get(self, payload: dict) -> dict:
        service_name = payload.get("serviceName")
        if not service_name:
            raise ValueError("Payload precisa conter a chave 'serviceName'")
        url = f"{BASE_URL}?serviceName={service_name}&outputType=json"
        response = requests.get(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def post(self, payload: dict) -> dict:
        service_name = payload.get("serviceName")
        if not service_name:
            raise ValueError("Payload precisa conter a chave 'serviceName'")
        url = f"{BASE_URL}?serviceName={service_name}&outputType=json"
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()
