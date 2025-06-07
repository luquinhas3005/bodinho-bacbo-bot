from flask import Flask
import threading
import time
import requests
import os
from bs4 import BeautifulSoup
from telegram import Bot

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot está rodando!"

# Configurações do bot
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL_BACBO = "https://www.betano.bet.br/casino/live/games/bac-bo/5605/tables/"

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("Erro: TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definido.")
    exit()

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

def iniciar_bot():
    global último_resultado
    while True:
        resultado = extrair_resultado()
        if resultado and resultado != último_resultado:
            último_resultado = resultado
            resultados.append(resultado)

            sinais = detectar_padroes(resultados)
            for sinal in sinais:
                mensagem = f"
