import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ["TOKEN"]
ADMIN_ID = int(os.environ["ADMIN_ID"])
