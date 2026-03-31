import requests
import os
import asyncio
import psycopg2
from telegram import Bot

# --- ENV ---
TOKEN = os.getenv("TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
DATABASE_URL = os.getenv("DATABASE_URL")

bot = Bot(token=TOKEN)

# --- DB CONNECTION ---
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# crea tabella se non esiste
cur.execute("""
CREATE TABLE IF NOT EXISTS prezzi (
    id SERIAL PRIMARY KEY,
    prezzo REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# --- FUNZIONI DATABASE ---
def salva_prezzo(prezzo):
    cur.execute("INSERT INTO prezzi (prezzo) VALUES (%s)", (prezzo,))
    
    # mantiene solo ultimi 500
    cur.execute("""
        DELETE FROM prezzi
        WHERE id NOT IN (
            SELECT id FROM prezzi
            ORDER BY timestamp DESC
            LIMIT 500
        )
    """)
    
    conn.commit()

def prendi_storico(limit=500):
    cur.execute("""
        SELECT prezzo FROM prezzi
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    
    rows = cur.fetchall()
    return [r[0] for r in rows][::-1]

# --- API HYPIXEL ---
def get_prezzo():
    url = "https://api.hypixel.net/skyblock/bazaar"
    data = requests.get(url).json()

    sell_orders = data["products"]["ENCHANTED_MYCELIUM"]["sell_summary"]
    prezzo_lordo = sell_orders[0]["pricePerUnit"]

    TAX = 0.011
    prezzo_netto = prezzo_lordo * (1 - TAX)

    return prezzo_netto, prezzo_lordo

# --- MAIN ---
async def main():
    while True:
        try:
            prezzo_netto, prezzo_lordo = get_prezzo()

            salva_prezzo(prezzo_lordo)
            storico = prendi_storico()

            if len(storico) < 20:
                await asyncio.sleep(60)
                continue

            media_breve = sum(storico[-20:]) / 20
            media_lunga = sum(storico) / len(storico)

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

            # manda SEMPRE ogni 10 minuti
            await bot.send_message(chat_id=CHAT_ID, text=messaggio)

            await asyncio.sleep(600)

        except Exception as e:
            print("Errore:", e)
            await asyncio.sleep(60)

asyncio.run(main())
