import requests
import time
from telegram import Bot
import os
TOKEN =os.environ.get("TOKEN")
CHAT_ID = os.environ.get("CHAT_ID)

bot = Bot(token=TOKEN)

storico = []

def get_prezzo():
    url = "https://api.hypixel.net/skyblock/bazaar"
    data = requests.get(url).json()

    prodotto = data["products"]["ENCHANTED_MYCELIUM"]
    prezzo = prodotto["quick_status"]["sellPrice"]

    return prezzo

def controlla():
    prezzo = get_prezzo()
    storico.append(prezzo)

    if len(storico) > 30:
        storico.pop(0)

    media = sum(storico) / len(storico)

    print(f"{prezzo:.2f} | media {media:.2f}")

    if prezzo > media * 1.15:
        bot.send_message(
            chat_id=CHAT_ID,
            text=f"🔥 VENDI ENCHANTED MYCELIUM!\nPrezzo: {prezzo:.2f}\nMedia: {media:.2f}"
        )

while True:
    controlla()
    time.sleep(300)
