from flask import Flask
import threading
import requests
import time
import os
from bs4 import BeautifulSoup
from telegram import Bot

app = Flask(__name__)

# Configurações do bot
TELEGRAM_TOKEN = os.environ.get("8084723198:AAGDxbmNHaRMoJ8k5ciPOhLbRFDUOS0toko
")
TELEGRAM_CHAT_ID = os.environ.get("
-1002740925115
")
URL_BACBO = "https://www.betano.bet.br/casino/live/games/bac-bo/5605/tables/"

bot = Bot(token=TELEGRAM_TOKEN)

resultados = []
último_resultado = None

def extrair_resultado():
    try:
        response = requests.get(URL_BACBO)
        soup = BeautifulSoup(response.text, "html.parser")
        item = soup.select_one('ul > li:nth-child(3) > div')
        if item:
            return item.text.strip()
    except Exception as e:
        print("Erro ao extrair:", e)
    return None

def detectar_padroes(historico):
    sinais = []
    if len(historico) < 5:
        return sinais

    padrao = historico[-3:]
    if padrao[0] != padrao[1] and padrao[1] != padrao[2]:
        sinais.append("Alternância detectada")

    return sinais

def enviar_sinal(mensagem):
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=mensagem)
        print("Sinal enviado:", mensagem)
    except Exception as e:
        print("Erro ao enviar sinal:", e)

def loop_bot():
    global último_resultado
    while True:
        resultado = extrair_resultado()
        if resultado and resultado != último_resultado:
            último_resultado = resultado
            resultados.append(resultado)

            sinais = detectar_padroes(resultados)
            for sinal in sinais:
                mensagem = f"🔔 {sinal}\nÚltimo: {resultado}"
                enviar_sinal(mensagem)
        else:
            print("Aguardando novo resultado...")
        time.sleep(10)

@app.route('/')
def home():
    return "✅ Bot Bac Bo está rodando!"

if __name__ == "__main__":
    threading.Thread(target=loop_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
