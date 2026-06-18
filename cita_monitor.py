import requests
import time
import logging
from datetime import datetime

# ─── НАСТРОЙКИ ───────────────────────────────────────────────
TELEGRAM_TOKEN = "8899954769:AAFU88AMEbKSl3ObT2k6cxlCxy41bk9AUso"
TELEGRAM_CHAT_ID = "337255924"

NIE = "Y7591779E"
NOMBRE = "VLADIMIR BORISOV"
PAIS_NAC = "149"                      # 149 = Russia

CHECK_INTERVAL = 60  # секунд между проверками
# ─────────────────────────────────────────────────────────────
