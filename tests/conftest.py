"""Конфигурация pytest."""
import pytest
from typing import Generator
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config.settings import Settings
from api.api_client import APIClient
import os
import sys


def pytest_addoption(parser) -> None:
    """Добавить опции командной строки."""
    parser.addoption(
        "--mode",
        action="store",
        default="all",
        help="Режим запуска: ui, api, all"
    )
    parser.addoption(
        "--browser",
        action="store",
        default=Settings.BROWSER,
        help="Браузер для UI тестов"
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=Settings.HEADLESS,
        help="Запуск в headless режиме"
    )


def pytest_configure(config) -> None:
    """Конфигурация перед запуском тестов."""
    config.addinivalue_line("markers", "ui: UI тесты")
    config.addinivalue_line("markers", "api: API тесты")


def pytest_collection_modifyitems(config, items) -> None:
    """Фильтрация тестов по режиму запуска."""
    mode = config.getoption("--mode")

    if mode == "ui":
        skip_api = pytest.mark.skip(reason="Запуск только UI тестов")
        for item in items:
            if "api" in item.keywords:
                item.add_marker(skip_api)
    elif mode == "api":
        skip_ui = pytest.mark.skip(reason="Запуск только API тестов")
        for item in items:
            if "ui" in item.keywords:
                item.add_marker(skip_ui)


@pytest.fixture(scope="function")
def driver(request) -> Generator[webdriver.Chrome, None, None]:
    """
    Фикстура для создания WebDriver.

    Args:
        request: Объект запроса pytest

    Yields:
        webdriver.Chrome: Экземпляр Chrome WebDriver
    """
    chrome_options = Options()
    
    # Базовые опции для стабильности
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Отключаем уведомления
    chrome_options.add_experimental_option(
        "prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0
        }
    )
    
    # User-Agent
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Отключаем автоматизацию
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    if request.config.getoption("--headless"):
        chrome_options.add_argument("--headless=new")
    
    # Используем webdriver_manager для автоматической загрузки драйвера
    try:
        driver_path = ChromeDriverManager().install()
        
        # Проверяем, что драйвер существует и исполняемый
        if not os.path.exists(driver_path):
            raise FileNotFoundError(f"ChromeDriver not found at {driver_path}")
        
        service = Service(executable_path=driver_path)
        driver_instance = webdriver.Chrome(service=service, options=chrome_options)
        
    except Exception as e:
        # Если webdriver_manager не сработал, пробуем системный chromedriver
        try:
            driver_instance = webdriver.Chrome(options=chrome_options)
        except Exception as e2:
            pytest.skip(
                f"ChromeDriver не найден. Установите ChromeDriver: "
                f"https://chromedriver.chromium.org/\n"
                f"Ошибка webdriver_manager: {e}\n"
                f"Ошибка системного драйвера: {e2}"
            )
            return
    
    driver_instance.implicitly_wait(Settings.IMPLICIT_WAIT)
    driver_instance.set_page_load_timeout(Settings.PAGE_LOAD_TIMEOUT)
    
    yield driver_instance
    
    try:
        driver_instance.quit()
    except Exception:
        pass


@pytest.fixture(scope="function")
def api_client() -> APIClient:
    """
    Фикстура для API клиента.

    Returns:
        APIClient: Экземпляр API клиента
    """
    return APIClient()
