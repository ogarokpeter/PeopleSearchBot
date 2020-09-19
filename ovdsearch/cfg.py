import os


class Config:
    def __init__(self):
        self.telegram_token = os.environ.get("BOT_TOKEN")
        self.db_url = os.environ.get("DB_URL")

    def check(self):
        if not self.telegram_token:
            raise SystemExit(
                "Передайте токен бота через переменную окружения 'BOT_TOKEN'"
            )
        if not self.db_url:
            raise SystemExit("Передайте URL для подключения к БД через 'DB_URL'")
