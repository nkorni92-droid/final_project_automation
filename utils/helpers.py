"""Вспомогательные утилиты."""
import json
import time
from typing import Any, Dict, Optional
from selenium.webdriver.remote.webdriver import WebDriver
import allure


class Helpers:
    """Вспомогательные методы для тестов."""

    @staticmethod
    @allure.step("Сохранить скриншот")
    def take_screenshot(
        driver: WebDriver,
        name: str = "screenshot"
    ) -> None:
        """
        Сделать скриншот и прикрепить к отчету.

        Args:
            driver: WebDriver
            name: Название скриншота
        """
        screenshot = driver.get_screenshot_as_png()
        allure.attach(
            screenshot,
            name,
            allure.attachment_type.PNG
        )

    @staticmethod
    @allure.step("Сохранить JSON данные")
    def attach_json(data: Any, name: str = "data") -> None:
        """
        Прикрепить JSON данные к отчету.

        Args:
            data: Данные для прикрепления
            name: Название вложения
        """
        allure.attach(
            json.dumps(data, indent=2, ensure_ascii=False),
            name,
            allure.attachment_type.JSON
        )

    @staticmethod
    def wait_for_condition(
        condition_func,
        timeout: int = 10,
        interval: float = 0.5,
        message: str = "Condition not met"
    ) -> bool:
        """
        Ожидание выполнения условия.

        Args:
            condition_func: Функция-условие
            timeout: Таймаут в секундах
            interval: Интервал проверки
            message: Сообщение при ошибке

        Returns:
            bool: True если условие выполнено

        Raises:
            TimeoutError: Если условие не выполнено за отведенное время
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            if condition_func():
                return True
            time.sleep(interval)
        raise TimeoutError(message)
