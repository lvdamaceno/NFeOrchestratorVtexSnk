# Orquestrador NFe VTEX ↔ Sankhya

Serviço Python leve para automatizar a integração entre pedidos da loja VTEX e o ERP Sankhya, sincronizando clientes, criando e faturando pedidos, e enviando os XMLs de NFe de volta à VTEX.

## 🚀 Funcionalidades

- **Integração VTEX**: Busca pedidos e dados de clientes via API VTEX
- **Sincronização de Clientes**: Verifica se o cliente existe no Sankhya; atualiza cadastro ou cria novo registro
- **Gerenciamento de Pedidos**: Cria pedido no Sankhya, confirma e fatura
- **Tratamento de NFe**: Recupera o XML de NFe gerado pelo Sankhya
- **Envio de Nota à VTEX**: Aguarda sua confirmação antes de enviar o XML de volta à VTEX
- **Logging Configurável**: Níveis DEBUG ou INFO controlados por variável de ambiente

## 🛠 Tecnologias

- **Python 3.9+**
- **requests** para requisições HTTP
- **python-dotenv** para variáveis de ambiente
- **módulo logging** para registro estruturado de logs

## 📦 Instalação

1. **Clone o repositório**:
   ```bash
   git clone https://github.com/SEU_USUARIO/NFeOrchestratorVtexSnk.git
   cd NFeOrchestratorVtexSnk
   ```

2. **Crie e ative um ambiente virtual**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate   # Linux/macOS
   .venv\Scripts\activate    # Windows
   ```

3. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

## 🔧 Configuração

1. **Variáveis de ambiente**: Edite o arquivo `.env` na raiz:
   ```ini
   VTEX_APP_KEY=
   VTEX_APP_TOKEN=
   VTEX_ACCOUNT=

   SANKHYA_TOKEN=
   SANKHYA_APPKEY=
   SANKHYA_USERNAME=
   SANKHYA_PASSWORD=

   APP_ENV=0   # 0 = logs DEBUG, 1 = logs INFO
   ```

2. **Logging**: Em produção, defina `APP_ENV=1` para menos verbosidade.

## ▶️ Uso

1. **Defina o ID do pedido**: Ajuste a variável `vtex_order_id` em `main.py` ou modifique para receber argumento de linha de comando.
2. **Execute o orquestrador**:
   ```bash
   python main.py
   ```

O fluxo será:
1. Buscar detalhes de pedido e cliente na VTEX
2. Sincronizar cadastro do cliente no Sankhya (criar ou atualizar)
3. Criar, confirmar e faturar o pedido no Sankhya
4. Recuperar o XML de NFe
5. Solicitar sua confirmação antes de enviar para a VTEX
6. Enviar o XML de volta à VTEX para concluir o processo

## 🗂 Estrutura do Projeto

```plaintext
NFeOrchestratorVtexSnk/
├── .env                  # Variáveis de ambiente
├── requirements.txt      # Dependências Python
├── main.py               # Ponto de entrada da orquestração
├── utils.py              # Configuração de logging e utilitários
├── vtex_api/             # Módulo de integração VTEX
│   ├── fetch.py          # Busca de pedidos e clientes
│   ├── builders.py       # Montagem de payloads VTEX
│   ├── invoice.py        # Envio de XML de nota à VTEX
│   └── utils.py          # Funções auxiliares VTEX
└── sankhya_api/          # Módulo de integração Sankhya
    ├── auth.py           # Autenticação e sessão
    ├── fetch.py          # Recuperação de XML de NFe
    ├── insert.py         # Inserção/atualização de clientes e pedidos
    ├── update.py         # Confirmação e faturamento de pedidos
    └── utils.py          # Funções auxiliares Sankhya
``` 

## 🤝 Contribuição

Contribuições, issues e sugestões de funcionalidades são bem-vindas! Abra uma issue ou envie um pull request.

## 📄 Licença

Este projeto está licenciado sob a MIT License. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
