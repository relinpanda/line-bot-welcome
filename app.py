# app.py
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent
import os

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ.get('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.environ.get('LINE_CHANNEL_SECRET'))

@app.route("/")
def home():
    return "Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    welcome_message = """歡迎加入本群組！
⏰ 服務時間：週一至週五 9:00-18:00（午休 12:00-13:30）

📝 提供資料更新時，請說明：
• 更新位置：選單名稱/頁面位置
• 檔案範圍：需處理的頁數或範圍

💡 為確保專案順利進行並控制成本，建議：
• 先進行內部討論與確認
• 再提供最終版本資料
• 避免反覆修改而增加額外費用"""
    
    try:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=welcome_message)
        )
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))