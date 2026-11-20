import os
from dotenv import load_dotenv
load_dotenv()
APP_NAME = os.getenv("APP_NAME", "Tip Checkpoint API")
DB_PATH = os.getenv("DB_PATH", "app/data/tip_checkpoint.db")
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
