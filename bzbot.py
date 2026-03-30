import requests
import time
import os
import asyncio
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID")) 


bot = Bot(token=TOKEN)

storico = []

def get_prezzo():
    url = "https://api.hypixel.net/skyblock/bazaar"
    data = requests.get(url).json()

    sell_orders = data["products"]["ENCHANTED_MYCELIUM"]["sell_summary"]
    prezzo_lordo = sell_orders[0]["pricePerUnit"]

    TAX = 0.011
    prezzo_netto = prezzo_lordo * (1 - TAX)

    return prezzo_netto, prezzo_lordo

async def main():
    ultimo_stato = ""

    while True:
        prezzo_netto, prezzo_lordo = get_prezzo()
        storico.append(prezzo_lordo)

        # memoria lunga
        if len(storico) > 500:
            storico.pop(0)

        # aspetta abbastanza dati
        if len(storico) < 20:
            await asyncio.sleep(60)
            continue

        # media breve e lunga
        media_breve = sum(storico[-20:]) / 20
        media_lunga = sum(storico) / len(storico)

        # logica intelligente
        if prezzo_lordo > media_lunga * 1.05 and media_breve < media_lunga:
            stato = "🔴 VENDI (picco)"
        elif media_breve > media_lunga:
            stato = "🟡 HOLD (sale)"
        else:
            stato = "🟡 HOLD"

        messaggio = (
            f"{stato}\n"
            f"Prezzo netto: {prezzo_netto:.2f}\n"
            f"Prezzo lordo: {prezzo_lordo:.2f}\n"
            f"Media breve: {media_breve:.2f}\n"
            f"Media lunga: {media_lunga:.2f}"
        )

        print(messaggio)

        # evita spam (manda solo se cambia stato)
        if stato != ultimo_stato:
            await bot.send_message(chat_id=CHAT_ID, text=messaggio)
            ultimo_stato = stato

        await asyncio.sleep(300)

asyncio.run(main())

