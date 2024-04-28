from dotenv import load_dotenv
import os
load_dotenv()
from sarufi import Sarufi
api_key = os.getenv("API_KEY")
bot_id = os.getenv("BOT_ID")
sarufi = Sarufi(api_key)
sarufi.chat(bot_id ,message="Habari")