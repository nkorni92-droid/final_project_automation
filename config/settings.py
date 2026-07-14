"""Настройки окружения и URL."""
import os
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Класс с настройками проекта."""

    # URL
    BASE_URL: str = os.getenv("BASE_URL", "https://www.chitai-gorod.ru")
    API_URL: str = os.getenv("API_URL", "https://www.chitai-gorod.ru")

    # Timeouts
    IMPLICIT_WAIT: int = int(os.getenv("IMPLICIT_WAIT", "10"))
    EXPLICIT_WAIT: int = int(os.getenv("EXPLICIT_WAIT", "20"))
    PAGE_LOAD_TIMEOUT: int = int(os.getenv("PAGE_LOAD_TIMEOUT", "30"))

    # Browser
    BROWSER: str = os.getenv("BROWSER", "chrome")
    HEADLESS: bool = os.getenv("HEADLESS", "False").lower() == "true"

    # Auth
    TOKEN: Optional[str] = os.getenv("TOKEN")

    @staticmethod
    def get_headers() -> Dict[str, str]:
        """Получить заголовки для API запросов."""
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
        }
        
        if Settings.TOKEN:
            headers["Authorization"] = f"Bearer {Settings.TOKEN}"
        
        return headers
