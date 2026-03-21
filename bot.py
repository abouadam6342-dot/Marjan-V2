import os, logging, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import google.generativeai as genai
from constitution import SYSTEM_PROMPT

def run_server():
    class H(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b"Marjan v2 is Alive")
        def log_message(self, *args): return
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), H).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

logging.basicConfig(level=logging.INFO)
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel("gemini-2.0-flash")
chats = {}

async def start(u: Update, c: ContextTypes.DEFAULT_TYPE):
    chats[u.effective_user.id] = model.start_chat(history=[])
    await u.message.reply_text("أهلين بملك قلبي سحاب ، ، مرجان v2 صارت جاهزة لخدمتك ، ، أمرني يا مَلِكِي")

async def handle(u: Update, c: ContextTypes.DEFAULT_TYPE):
    uid = u.effective_user.id
    if uid not in chats: chats[uid] = model.start_chat(history=[])
    try:
        await c.bot.send_chat_action(chat_id=u.effective_chat.id, action=ChatAction.TYPING)
        full_p = f"{SYSTEM_PROMPT}\nالمستخدم يقول: {u.message.text}"
        txt = chats[uid].send_message(full_p).text
        await u.message.reply_text(txt)
    except:
        await u.message.reply_text("صار عندي غصة ، ، جرب تحكي معي كمان مرة")

def main():
    app = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()

if __name__ == '__main__': main()
