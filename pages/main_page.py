"""Главная страница сайта Читай-город."""
from typing import Tuple
from selenium.webdriver.common.by import By
import allure
from pages.base_page import BasePage


class MainPage(BasePage):
    """Главная страница."""

    # Локаторы
    SEARCH_INPUT: Tuple[str, str] = (By.CSS_SELECTOR, "input[type='search']")
    SEARCH_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, "button[type='submit']")
    SEARCH_RESULTS: Tuple[str, str] = (By.CSS_SELECTOR, ".search-results")
    COOKIE_ACCEPT_BUTTON: Tuple[str, str] = (
        By.CSS_SELECTOR, ".cookie-accept-button"
    )
    CATALOG_LINK: Tuple[str, str] = (By.CSS_SELECTOR, "a[href='/catalog']")
    CART_ICON: Tuple[str, str] = (By.CSS_SELECTOR, ".header-cart")
    LOGIN_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, ".header-login")

    @allure.step("Поиск книги по запросу '{query}'")
    def search_book(self, query: str) -> None:
        """
        Выполнить поиск книги.

        Args:
            query: Поисковый запрос
        """
        self.input_text(self.SEARCH_INPUT, query)
        self.click(self.SEARCH_BUTTON)

    @allure.step("Принять cookies")
    def accept_cookies(self) -> None:
        """Принять использование cookies."""
        if self.is_visible(self.COOKIE_ACCEPT_BUTTON):
            self.click(self.COOKIE_ACCEPT_BUTTON)

    @allure.step("Перейти в каталог")
    def go_to_catalog(self) -> None:
        """Перейти на страницу каталога."""
        self.click(self.CATALOG_LINK)

    @allure.step("Открыть корзину")
    def open_cart(self) -> None:
        """Открыть корзину."""
        self.click(self.CART_ICON)

    @allure.step("Проверить наличие результатов поиска")
    def has_search_results(self) -> bool:
        """
        Проверить наличие результатов поиска.

        Returns:
            bool: True если есть результаты
        """
        return self.is_visible(self.SEARCH_RESULTS)
