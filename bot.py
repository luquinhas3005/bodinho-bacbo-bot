from flask import Flask
import threading
import requests
import time
import os
from bs4 import BeautifulSoup
from telegram import Bot

app = Flask(__name__)

# Configurações do bot
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
URL_BACBO = "https://www.betano.bet.br/casino/live/games/bac-bo/5605/tables/"

bot = Bot(token=TELEGRAM_TOKEN)

resultados = []
último_resultado = None

def extrair_resultado():
    print("🔍 Tentando extrair resultado do site...")
    try:
        response = requests.get(URL_BACBO)
        soup = BeautifulSoup(response.text, "html.parser")
        item = soup.select_one('ul > li:nth-child(3) > div')
        if item:
            resultado = item.text.strip()
            print(f"🎯 Resultado extraído: {resultado}")
            return resultado
        else:
            print("⚠️ Elemento do resultado não encontrado.")
    except Exception as e:
        print("❌ Erro ao extrair:", e)
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
        print("📤 Sinal enviado:", mensagem)
    except Exception as e:
        print("❌ Erro ao enviar sinal:", e)

def loop_bot():
    global último_resultado
    time.sleep(5)  # Aguarda o servidor iniciar

    # Envio de sinal forçado (teste)
    enviar_sinal("🔧 Teste de sinal automático: bot rodando com sucesso!")

    while True:
        resultado = extrair_resultado()
        if resultado and resultado != último_resultado:
            último_resultado = resultado
            resultados.append(resultado)
            print("📈 Histórico atualizado:", resultados)

            sinais = detectar_padroes(resultados)
            for sinal in sinais:
                mensagem = f"🔔 {sinal}\nÚltimo: {resultado}"
                enviar_sinal(mensagem)
        else:
            print("⏳ Aguardando novo resultado ou sem mudança...")
        time.sleep(10)

@app.route('/')
def home():
    return "✅ Bot Bac Bo está rodando com scraping e Telegram!"

if __name__ == "__main__":
    threading.Thread(target=loop_bot).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
