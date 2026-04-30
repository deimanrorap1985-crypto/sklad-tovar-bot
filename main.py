import requests
import time
import re
import os

API_URL = "https://platform-api.max.ru"
TOKEN = os.getenv("TOKEN")

headers = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

print("🚀 BOT STARTED ON RAILWAY v3")

board = []
offset = 0

while True:
    try:
        r = requests.get(
            f"{API_URL}/updates?offset={offset}&limit=20", 
            headers=headers, 
            timeout=30   # увеличил таймаут
        )
        
        if r.status_code == 200:
            for update in r.json().get("result", []):
                offset = update.get("update_id", 0) + 1

                if update.get("update_type") == "message_created":
                    msg = update.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = str(msg.get("body", {}).get("text", "") or msg.get("text", "")).strip()

                    print(f"📩 Получено: {text}")

                    if text in ["/доска", "/board", "/startboard"]:
                        data = {"text": "📦 ДОСКА ЗАКАЗОВ СОЗДАНА\n\nКидай номера заказов"}
                        requests.post(f"{API_URL}/messages?chat_id={chat_id}", headers=headers, json=data)
                        print("✅ Доска отправлена")

                    elif re.search(r'\b\d{4,}\b', text):
                        order_id = re.search(r'\b(\d{4,})\b', text).group(1)
                        if not any(o.get("id") == order_id for o in board):
                            board.append({"id": order_id, "taken_by": None, "done_by": None})
                            print(f"✅ Заказ {order_id} добавлен")
                            data = {"text": f"✅ Заказ {order_id} добавлен в доску"}
                            requests.post(f"{API_URL}/messages?chat_id={chat_id}", headers=headers, json=data)

    except requests.exceptions.Timeout:
        print("⏳ Timeout - продолжаем...")
        time.sleep(5)
        continue
    except Exception as e:
        print("Ошибка:", str(e)[:100])
        time.sleep(5)

    time.sleep(1)
