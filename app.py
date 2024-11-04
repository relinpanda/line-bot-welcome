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
⏰ 服務時間與回應
．服務時間：週一至週五 9:00-18:00、午休 12:00-13:30
．我們會在工作時間內，盡快處理您的需求
．當天的訊息，通常當天下班前會處理，若更新內容過多或是太晚提供，會於隔天繼續處理
．若在非上班時段收到您的訊息，我們會在下個工作日處理
．因為 tag 人員會有音效，深夜或清晨請儘量避免此功能 (除非緊急狀況)，我們每天都會巡視群組訊息，請放心
 
📝 資料更新說明
提供上架資料時，請同時提供以下訊息：
．更新位置：請標明［選單名稱 / 頁面位置］或提供［該頁網址連結］
．檔案範圍：請標明需處理的頁數或範圍
．請勿傳未整理過的檔案，訂正資訊、資料蒐集、內容撰寫不在我們處理範圍內，請見諒

溫馨提醒：若同頁面資料大量、多次修改，會產生額外的費用、延長製作時程，為確保專案順利進行並控制在預算，建議先內部確認後再提供最終版本，感謝配合🙏"""
    
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