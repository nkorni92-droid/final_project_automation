"""Базовый класс для всех страниц."""
from typing import Optional, Tuple, List
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import allure
from config.settings import Settings


class BasePage:
    """Базовый класс для Page Object Model."""

    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализация базовой страницы.

        Args:
            driver: Экземпляр WebDriver
        """
        self.driver = driver
        self.wait = WebDriverWait(driver, Settings.EXPLICIT_WAIT)
        self.base_url = Settings.BASE_URL

    @allure.step("Открыть страницу {url}")
    def open(self, url: str = "") -> None:
        """
        Открыть страницу по URL.

        Args:
            url: Относительный или абсолютный URL
        """
        if url.startswith("http"):
            self.driver.get(url)
        else:
            self.driver.get(f"{self.base_url}{url}")

    @allure.step("Найти элемент {locator}")
    def find_element(self, locator: Tuple[str, str]) -> WebElement:
        """
        Найти элемент на странице.

        Args:
            locator: Кортеж (стратегия, значение)

        Returns:
            WebElement: Найденный элемент

        Raises:
            TimeoutException: Если элемент не найден
        """
        return self.wait.until(
            EC.presence_of_element_located(locator)
        )

    @allure.step("Найти элементы {locator}")
    def find_elements(self, locator: Tuple[str, str]) -> List[WebElement]:
        """
        Найти все элементы по локатору.

        Args:
            locator: Кортеж (стратегия, значение)

        Returns:
            List[WebElement]: Список найденных элементов
        """
        return self.wait.until(
            EC.presence_of_all_elements_located(locator)
        )

    @allure.step("Кликнуть по элементу {locator}")
    def click(self, locator: Tuple[str, str]) -> None:
        """
        Кликнуть по элементу.

        Args:
            locator: Кортеж (стратегия, значение)
        """
        element = self.wait.until(
            EC.element_to_be_clickable(locator)
        )
        element.click()

    @allure.step("Ввести текст '{text}' в элемент {locator}")
    def input_text(self, locator: Tuple[str, str], text: str) -> None:
        """
        Ввести текст в поле.

        Args:
            locator: Кортеж (стратегия, значение)
            text: Текст для ввода
        """
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)

    @allure.step("Получить текст элемента {locator}")
    def get_text(self, locator: Tuple[str, str]) -> str:
        """
        Получить текст элемента.

        Args:
            locator: Кортеж (стратегия, значение)

        Returns:
            str: Текст элемента
        """
        return self.find_element(locator).text

    @allure.step("Проверить видимость элемента {locator}")
    def is_visible(self, locator: Tuple[str, str]) -> bool:
        """
        Проверить, видим ли элемент.

        Args:
            locator: Кортеж (стратегия, значение)

        Returns:
            bool: True если элемент видим
        """
        try:
            return self.wait.until(
                EC.visibility_of_element_located(locator)
            ).is_displayed()
        except TimeoutException:
            return False

    @allure.step("Добавить cookie в браузер")
    def add_cookie(self, name: str, value: str) -> None:
        """
        Добавить cookie в браузер.

        Args:
            name: Имя cookie
            value: Значение cookie
        """
        self.driver.add_cookie({"name": name, "value": value})
