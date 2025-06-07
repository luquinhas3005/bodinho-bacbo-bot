from flask import Flask
import threading
import requests
import time
import os
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio

app = Flask(__name__)

# Configuração do bot
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL_BACBO = "https://www.betano.bet.br/casino/live/games/bac-bo/5605/tables/"

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Erro: TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidos.")
    exit(1)

bot = Bot(token=TELEGRAM_TOKEN)
resultados = []
último_resultado = None

def extrair_resultado():
    print("🔍 Extraindo resultado da mesa...")
    try:
        resp = requests.get(URL_BACBO, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        item = soup.select_one("ul > li:nth-child(3) > div")
        if item:
            valor = item.text.strip()
            print(f"🎯 Resultado extraído: {valor}")
            return valor
        else:
            print("⚠️ Elemento não encontrado no HTML.")
    except Exception as e:
        print("❌ Erro ao extrair resultado:", e)
    return None

def detectar_padroes(historico):
    sinais = []
    if len(historico) < 3:
        return sinais
    padrao = historico[-3:]
    if padrao[0] != padrao[1] and padrao[1] != padrao[2]:
        sinais.append("🔁 Alternância detectada")
    return sinais

def enviar_sinal(mensagem):
    try:
        asyncio.run(bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem))
        print("📤 Sinal enviado:", mensagem)
    except Exception as e:
        print("❌ Falha ao enviar sinal:", e)

def loop_bot():
    global último_resultado
    time.sleep(5)
    enviar_sinal("🧪 Teste automático: bot está ativo!")

    while True:
        resultado = extrair_resultado()
        if resultado and resultado != último_resultado:
            último_resultado = resultado
            resultados.append(resultado)
            print("📈 Histórico:", resultados)

            for sinal in detectar_padroes(resultados):
                enviar_sinal(f"🔔 {sinal}\nÚltimo resultado: {resultado}")
        else:
            print("⏳ Aguardando resultado novo...")
        time.sleep(10)

@app.route("/")
def home():
    return "✅ Bot Bac Bo está rodando."

if __name__ == "__main__":
    threading.Thread(target=loop_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))
