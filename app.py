from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, JoinEvent
import os
import logging
from time import sleep

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    logger.info("Request body: %s", body)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error("Invalid signature")
        abort(400)
    except Exception as e:
        logger.error("Error: %s", str(e))
        return 'OK'  # 即使發生錯誤也返回 OK
    return 'OK'

@handler.add(JoinEvent)
def handle_join(event):
    logger.info("Bot joined group/room")
    welcome_message = """歡迎加入本群組！
⏰ 服務時間：週一至週五 9:00-18:00（午休 12:00-13:30）

📝 提供資料更新時，請說明：
• 更新位置：選單名稱/頁面位置
• 檔案範圍：需處理的頁數或範圍

💡 為確保專案順利進行並控制成本，建議：
• 先進行內部討論與確認
• 再提供最終版本資料
• 避免反覆修改而增加額外費用"""
    
    # 添加重試機制
    max_retries = 3
    for attempt in range(max_retries):
        try:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=welcome_message)
            )
            logger.info("Welcome message sent successfully")
            break
        except LineBotApiError as e:
            logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                sleep(1)  # 等待1秒後重試
            else:
                logger.error("Max retries reached, giving up")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            break

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))