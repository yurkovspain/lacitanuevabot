import requests
import time
import logging
from datetime import datetime

TELEGRAM_TOKEN = "8899954769:AAFU88AMEbKSl3ObT2k6cxlCxy41bk9AUso"
TELEGRAM_CHAT_ID = "337255924"
NIE = "Y7591779E"
NOMBRE = "VLADIMIR BORISOV"
PAIS_NAC = "149"
CHECK_INTERVAL = 60

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s", handlers=[logging.FileHandler("cita_monitor.log"), logging.StreamHandler()])

BASE_URL = "https://icp.administracionelectronica.gob.es/icpco"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "es-ES,es;q=0.9", "Connection": "keep-alive", "Upgrade-Insecure-Requests": "1"}

def send_telegram(message):
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10).raise_for_status()
    except Exception as e:
        logging.error(f"Telegram error: {e}")

def check_cita():
    session = requests.Session()
    session.headers.update(HEADERS)
    try:
        session.get(f"{BASE_URL}/acEntrada", timeout=15)
        session.post(f"{BASE_URL}/acEntrada", data={"accion": "4", "codProvincia": "03", "codTramite": "4094", "rdbTipoTramite": "4"}, timeout=15)
        session.post(f"{BASE_URL}/acValidarEntrada", data={"rdbTipoDoc": "N.I.E.", "txtIdCitado": NIE, "txtDesCitado": NOMBRE, "txtPaisNac": PAIS_NAC}, timeout=15)
        r = session.post(f"{BASE_URL}/acCitar", data={"accion": "citarme"}, timeout=15)
        html = r.text.lower()
        if any(p in html for p in ["no hay citas disponibles", "no existen citas", "no quedan citas"]):
            logging.info("Слотов нет")
            return False
        if any(p in html for p in ["seleccione", "fecha", "hora"]):
            logging.warning("СЛОТЫ НАЙДЕНЫ!")
            return True
