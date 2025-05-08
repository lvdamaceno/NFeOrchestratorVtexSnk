"""
Módulo responsável por consultar a API Sankhya com autenticação e retentativas automáticas.

Contém a classe SankhyaClient, que realiza autenticação via token Bearer e executa consultas SQL
através da API REST da Sankhya. Inclui mecanismos de revalidação do token em caso de expiração e
tratamento de erros de conexão com múltiplas tentativas controladas.

Dependências:
    - requests
    - os
    - time
    - logging
    - dotenv
    - SankhyaAuth (auth.py)
    - RequestError (exceção personalizada)
"""

import logging
import time
from datetime import datetime
from requests.exceptions import ReadTimeout, ConnectionError as RequestsConnectionError
import requests
from .auth import SankhyaAuth
from .exceptions import RequestError, SankhyaHTTPError


def log_tempo(msg=""):
    """Loga uma mensagem com timestamp atual para medir performance."""
    print(f"{datetime.now()} - {msg}")


class SankhyaClient:  # pylint: disable=too-few-public-methods
    """
    Cliente para interação com a API Sankhya usando autenticação Bearer.

    Esta classe realiza requisições à API Sankhya para execução de comandos SQL,
    gerenciando automaticamente autenticação e tentativas de reconexão em caso de falhas.
    """

    def __init__(self, servicename, endpoint, retries, timeout=60):
        # log_tempo("Início da execução do SankhyaClient")
        self.auth = SankhyaAuth()

        self._token = None  # token será obtido apenas quando necessário
        self.endpoint = endpoint
        self.timeout = timeout
        self.retries = retries
        self.servicename = servicename

    @property
    def token(self):
        """Token autenticado, obtido sob demanda."""
        if not self._token:
            # log_tempo("Token ainda não foi obtido. Autenticando...")
            self._token = self.auth.authenticate()
            # log_tempo("Token obtido com sucesso")
        return self._token

    def _renew_token(self):
        """Renova e atualiza o token."""
        # log_tempo("Renovando token de autenticação")
        self._token = self.auth.authenticate()

    def load_cpf_records(self, cpf):
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}'
        }

        payload = {
            "serviceName": "CRUDServiceProvider.loadRecords",
            "requestBody": {
                "dataSet": {
                    "rootEntity": "Parceiro",
                    "includePresentationFields": "N",
                    "tryJoinedFields": "true",
                    "offsetPage": "0",
                    "criteria": {
                        "expression": {
                            "$": f"CGC_CPF = '{cpf}'"
                        }
                    },
                    "entity": [
                        {
                            "path": "",
                            "fieldset": {
                                "list": "NOMEPARC, CGC_CPF"
                            }
                        }
                    ]
                }
            }
        }

        for attempt in range(self.retries):
            try:
                logging.debug('Enviando requisição ao endpoint Sankhya (tentativa %d)', attempt + 1)

                response = requests.post(  # ← CORRIGIDO: POST em vez de GET
                    self.endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )

                logging.debug("Código de resposta: %s", response.status_code)

                if response.status_code == 200:
                    dados = response.json()
                    if 'responseBody' in dados:
                        return dados['responseBody']
                    else:
                        raise ValueError(f"Resposta inesperada: {dados}")

                elif response.status_code in (401, 403):
                    logging.warning("Token expirado ou inválido. Renovando token...")
                    self._renew_token()
                    headers["Authorization"] = f"Bearer {self.token}"
                    continue

                else:
                    raise SankhyaHTTPError(f"Erro HTTP {response.status_code}: {response.text}")

            except (ReadTimeout, RequestsConnectionError) as e:
                logging.warning("[%d/%d] Timeout ou erro de conexão: %s", attempt + 1, self.retries, e)
                time.sleep(5)

            except Exception as e:
                raise RequestError(f"Erro de conexão geral: {e}") from e

        raise RequestError("Falha após múltiplas tentativas de conexão.")

