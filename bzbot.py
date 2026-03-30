import requests
import time
from telegram import Bot
import os
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

storico = []

def get_prezzo():
    url = "https://api.hypixel.net/skyblock/bazaar"
    data = requests.get(url).json()
    return data["products"]["ENCHANTED_MYCELIUM"]["quick_status"]["sellPrice"]

while True:
    prezzo = get_prezzo()
    storico.append(prezzo)

    if len(storico) > 30:
        storico.pop(0)

    media = sum(storico) / len(storico)

    # decisione semplice
    if prezzo > media * 1.10:
        stato = "🔴 VENDI"
    else:
        stato = "🟡 HOLD"

    messaggio = f"{stato}\nPrezzo: {prezzo:.2f}\nMedia: {media:.2f}"

    print(messaggio)
    bot.send_message(chat_id=CHAT_ID, text=messaggio)

    time.sleep(300)  # ogni 5 min
