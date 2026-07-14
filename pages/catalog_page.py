"""Страница каталога."""
from typing import Tuple, List
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
import allure
from pages.base_page import BasePage


class CatalogPage(BasePage):
    """Страница каталога товаров."""

    # Локаторы
    PRODUCT_CARDS: Tuple[str, str] = (By.CSS_SELECTOR, ".product-card")
    PRODUCT_TITLE: Tuple[str, str] = (By.CSS_SELECTOR, ".product-title")
    PRODUCT_AUTHOR: Tuple[str, str] = (By.CSS_SELECTOR, ".product-author")
    PRODUCT_PRICE: Tuple[str, str] = (By.CSS_SELECTOR, ".product-price")
    ADD_TO_CART_BUTTON: Tuple[str, str] = (
        By.CSS_SELECTOR, ".add-to-cart-button"
    )
    SORT_DROPDOWN: Tuple[str, str] = (By.CSS_SELECTOR, ".sort-dropdown")
    FILTER_SIDEBAR: Tuple[str, str] = (By.CSS_SELECTOR, ".filter-sidebar")
    NEXT_PAGE: Tuple[str, str] = (By.CSS_SELECTOR, ".pagination-next")

    @allure.step("Получить список продуктов")
    def get_products(self) -> List[WebElement]:
        """
        Получить список всех продуктов на странице.

        Returns:
            List[WebElement]: Список элементов продуктов
        """
        return self.find_elements(self.PRODUCT_CARDS)

    @allure.step("Добавить первый продукт в корзину")
    def add_first_product_to_cart(self) -> None:
        """Добавить первый доступный продукт в корзину."""
        buttons = self.find_elements(self.ADD_TO_CART_BUTTON)
        if buttons:
            buttons[0].click()

    @allure.step("Получить название первого продукта")
    def get_first_product_title(self) -> str:
        """
        Получить название первого продукта.

        Returns:
            str: Название продукта
        """
        titles = self.find_elements(self.PRODUCT_TITLE)
        return titles[0].text if titles else ""

    @allure.step("Получить автора первого продукта")
    def get_first_product_author(self) -> str:
        """
        Получить автора первого продукта.

        Returns:
            str: Автор продукта
        """
        authors = self.find_elements(self.PRODUCT_AUTHOR)
        return authors[0].text if authors else ""

    @allure.step("Проверить, что автор '{expected_author}' в результатах")
    def is_author_in_results(self, expected_author: str) -> bool:
        """
        Проверить наличие автора в результатах поиска.

        Args:
            expected_author: Ожидаемый автор

        Returns:
            bool: True если автор найден
        """
        products = self.get_products()
        for product in products:
            author = product.find_element(*self.PRODUCT_AUTHOR).text
            if expected_author.lower() in author.lower():
                return True
        return False
