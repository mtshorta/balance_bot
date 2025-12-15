import os
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from pathlib import Path

# DEBUG: carregar .env exatamente da mesma pasta do script
env_path = Path(__file__).parent / ".env"
print("DEBUG: tentando carregar .env em:", env_path)
load_dotenv(dotenv_path=env_path)
print("DEBUG: SLACK_TOKEN após load_dotenv:", os.getenv("SLACK_TOKEN"))

SLACK_TOKEN = os.getenv("SLACK_TOKEN")
SLACK_CHANNEL = os.getenv("SLACK_CHANNEL")

contas = {
    "CRMV-GO": os.getenv("TOKEN_CRMV_GO"),
    "MAXBOT": os.getenv("TOKEN_MAXBOT"),
    "JUCEMG": os.getenv("TOKEN_JUCEMG"),
    "CRCRO": os.getenv("TOKEN_CRCRO"),
    "GUARATUBA": os.getenv("TOKEN_GUARATUBA"),
}

url = "https://app.maxbot.com.br/api/v1.php"
mensagens = []

def consultar_saldo(nome, token):
    payload = {
        "token": token,
        "cmd": "get_balance_gupshup"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == 1:
                saldo_str = data.get("currency_balance")
                valor_numerico = float(saldo_str.split()[0])
                mensagens.append((valor_numerico, nome, saldo_str))
            else:
                mensagens.append((float("-inf"), nome, f"Erro: {data.get('msg')}"))
        else:
            mensagens.append((float("-inf"), nome, f"Erro HTTP {response.status_code}"))
    except Exception as e:
        mensagens.append((float("-inf"), nome, f"Erro na requisição: {e}"))

def enviar_para_slack(mensagem, header="Saldos Gupshup 💰"):
    if not SLACK_TOKEN or not SLACK_CHANNEL:
        print("⚠️ SLACK_TOKEN ou SLACK_CHANNEL não configurados.")
        return

    client = WebClient(token=SLACK_TOKEN)
    try:
        client.chat_postMessage(
            channel=SLACK_CHANNEL,
            text=f"*{header}*\n{mensagem}"
        )
        print("✅ Mensagem enviada ao Slack com sucesso.")
    except SlackApiError as e:
        print(f"❌ Erro ao enviar mensagem: {e.response['error']}")

if __name__ == "__main__":
    for nome, token in contas.items():
        if not token:
            mensagens.append((float("-inf"), nome, "Token não configurado"))
            continue
        consultar_saldo(nome, token)

    mensagens.sort()
    mensagem_slack = "\n".join([f"*{nome}*: {saldo}" for _, nome, saldo in mensagens])
    print("Mensagem para o Slack:\n", mensagem_slack)
    enviar_para_slack(mensagem_slack)