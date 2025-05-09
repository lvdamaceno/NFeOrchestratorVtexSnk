# NFe Orchestrator VTEX → Sankhya

Este projeto realiza a integração entre pedidos da **VTEX** e o sistema **Sankhya**, automatizando a criação ou atualização de cadastros de clientes e a geração de notas fiscais eletrônicas (NFe).

## ⚙️ Funcionalidades

- Consulta de pedidos via API da VTEX
- Extração de dados do cliente e endereço de entrega
- Verificação e atualização/cadastro do cliente no Sankhya
- Geração e envio de NFe no ERP Sankhya
- Associação do pedido VTEX ao campo adicional da nota fiscal

## 📁 Estrutura Simplificada

```
NFeOrchestratorVtexSnk/
├── sankhya_api/
│   ├── auth.py
│   ├── fetch.py
│   └── utils.py
├── vtex_api/
│   └── fetch.py
├── main.py
├── .env
├── requirements.txt
```

## ▶️ Como executar

1. Clone este repositório
2. Crie um ambiente virtual:
   ```bash
   python3.9 -m venv venv
   source venv/bin/activate
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. Configure o arquivo `.env` com as credenciais VTEX e Sankhya
5. Execute o script principal:
   ```bash
   python main.py
   ```

## 🔐 Variáveis de ambiente (.env)

```env
VTEX_APPKEY=...
VTEX_APPTOKEN=...
SANKHYA_TOKEN=...
SANKHYA_APPKEY=...
SANKHYA_USERNAME=...
SANKHYA_PASSWORD=...
```

## 🧪 Requisitos

- Python 3.9
- Acesso às APIs da VTEX e Sankhya

## 📌 Observações

Este projeto está em evolução e possui foco prático para automatizar integrações comerciais entre sistemas distintos.

---

Desenvolvido com ❤️ para integração robusta entre e-commerce e ERP.
