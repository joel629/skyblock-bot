import requests
import time
import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

storico = []

def get_prezzo():
    url = "https://api.hypixel.net/skyblock/bazaar"
    data = requests.get(url).json()
    sell_orders=data["products"]["ENCHANTED_MYCELIUM"]["sell_summary"]
    prezzo_lordo = sell_orders[0]["pricePerUnit"]
    TAX= 0.011
    prezzo_netto=prezzo_lordo*(1-TAX)

    return prezzo_netto, prezzo_lordo

async def main():
    while True:
        prezzo_netto, prezzo_lordo = get_prezzo()
        storico.append(prezzo_lordo)

        if len(storico) > 30:
            storico.pop(0)

        media = sum(storico) / len(storico)

        if prezzo_lordo > media * 1.10:
            stato = "🔴 VENDI"
        else:
            stato = "🟡 HOLD"

        messaggio = f"{stato}\nPrezzo netto: {prezzo_netto:.2f}\nPrezzo lordo: {prezzo_lordo:.2f}\nMedia: {media:.2f}"

        print(messaggio)
        await bot.send_message(chat_id=CHAT_ID, text=messaggio)

        await asyncio.sleep(300)

asyncio.run(main())
