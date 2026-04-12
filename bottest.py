import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Dòng kiểm tra (Debug)
print(f"--- Debug ---")
print(f"Token: {TOKEN[:10]}... (độ dài: {len(TOKEN) if TOKEN else 0})")
print(f"Chat ID: {CHAT_ID}")
print(f"-------------")

if not TOKEN or not CHAT_ID:
    print("Lỗi: Không tìm thấy TOKEN hoặc CHAT_ID trong file .env!")
    exit()

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
message = "🚀 InsightFlow: Hệ thống đã sẵn sàng thu thập dữ liệu!"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": message}

response = requests.post(url, data=payload)
print(response.json())