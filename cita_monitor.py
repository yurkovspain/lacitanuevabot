logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("cita_monitor.log"),
        logging.StreamHandler()
    ]
)

BASE_URL = "https://icp.administracionelectronica.gob.es/icpco"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def send_telegram(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        r = requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": message}, timeout=10)
        r.raise_for_status()
        logging.info("Telegram уведомление отправлено")
    except Exception as e:
        logging.error(f"Ошибка Telegram: {e}")


def check_cita() -> bool:
    session = requests.Session()
    session.headers.update(HEADERS)

    try:
        r = session.get(f"{BASE_URL}/acEntrada", timeout=15)
        r.raise_for_status()

        data_entrada = {
            "accion": "4",
            "codProvincia": "03",
            "codTramite": "4094",
            "rdbTipoTramite": "4"
        }
        r = session.post(f"{BASE_URL}/acEntrada", data=data_entrada, timeout=15)
        r.raise_for_status()

        data_validar = {
            "rdbTipoDoc": "N.I.E.",
            "txtIdCitado": NIE,
            "txtDesCitado": NOMBRE,
            "txtPaisNac": PAIS_NAC,
        }
        r = session.post(f"{BASE_URL}/acValidarEntrada", data=data_validar, timeout=15)
        r.raise_for_status()

        r = session.post(f"{BASE_URL}/acCitar", data={"accion": "citarme"}, timeout=15)
        r.raise_for_status()

        html = r.text

        no_slots_phrases = [
            "no hay citas disponibles",
            "no existen citas disponibles",
            "no quedan citas",
        ]

        html_lower = html.lower()
        if any(phrase in html_lower for phrase in no_slots_phrases):
            logging.info("Слотов нет")
            return False

        if "seleccione" in html_lower or "fecha" in html_lower or "hora" in html_lower:
            logging.warning("🎉 СЛОТЫ НАЙДЕНЫ!")
            return True

        with open("last_response.html", "w", encoding="utf-8") as f:
            f.write(html)
        logging.info("Неизвестный ответ — сохранён в last_response.html")
        return False

    except requests.RequestException as e:
        logging.error(f"Ошибка запроса: {e}")
        return False


def main():
    logging.info("Мониторинг запущен")
    send_telegram("✅ Мониторинг cita Alicante (huellas) запущен. Жди уведомление когда появится слот.")

    attempt = 0
    while True:
        attempt += 1
        logging.info(f"Проверка #{attempt}")

        slots_found = check_cita()

        if slots_found:
            msg = (
                f"🚨 СЛОТ НАЙДЕН! #{attempt}\n"
                f"Срочно заходи на сайт и бронируй:\n"
                f"https://icp.administracionelectronica.gob.es/icpco/acEntrada\n\n"
                f"NIE: {NIE}\n"
                f"Имя: {NOMBRE}\n"
                f"Провинция: Alicante\n"
                f"Процедура: Toma de huellas TIE"
            )
            send_telegram(msg)
            time.sleep(30)
        else:
            time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
