"""Страница корзины."""
from typing import Tuple, List
from selenium.webdriver.common.by import By
import allure
from pages.base_page import BasePage


class CartPage(BasePage):
    """Страница корзины."""

    # Локаторы
    CART_ITEMS: Tuple[str, str] = (By.CSS_SELECTOR, ".cart-item")
    CART_EMPTY_MESSAGE: Tuple[str, str] = (By.CSS_SELECTOR, ".cart-empty")
    ITEM_TITLE: Tuple[str, str] = (By.CSS_SELECTOR, ".cart-item-title")
    ITEM_PRICE: Tuple[str, str] = (By.CSS_SELECTOR, ".cart-item-price")
    ITEM_QUANTITY: Tuple[str, str] = (By.CSS_SELECTOR, ".quantity-input")
    REMOVE_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, ".remove-item")
    TOTAL_PRICE: Tuple[str, str] = (By.CSS_SELECTOR, ".cart-total-price")
    CHECKOUT_BUTTON: Tuple[str, str] = (By.CSS_SELECTOR, ".checkout-button")
    CONTINUE_SHOPPING: Tuple[str, str] = (
        By.CSS_SELECTOR, ".continue-shopping"
    )

    @allure.step("Проверить, что корзина пуста")
    def is_cart_empty(self) -> bool:
        """
        Проверить, пуста ли корзина.

        Returns:
            bool: True если корзина пуста
        """
        return self.is_visible(self.CART_EMPTY_MESSAGE)

    @allure.step("Получить количество товаров в корзине")
    def get_items_count(self) -> int:
        """
        Получить количество товаров в корзине.

        Returns:
            int: Количество товаров
        """
        items = self.find_elements(self.CART_ITEMS)
        return len(items)

    @allure.step("Получить общую стоимость корзины")
    def get_total_price(self) -> str:
        """
        Получить общую стоимость корзины.

        Returns:
            str: Общая стоимость
        """
        return self.get_text(self.TOTAL_PRICE)

    @allure.step("Удалить первый товар из корзины")
    def remove_first_item(self) -> None:
        """Удалить первый товар из корзины."""
        buttons = self.find_elements(self.REMOVE_BUTTON)
        if buttons:
            buttons[0].click()

    @allure.step("Проверить наличие товара '{title}' в корзине")
    def has_item_with_title(self, title: str) -> bool:
        """
        Проверить наличие товара с указанным названием.

        Args:
            title: Название товара

        Returns:
            bool: True если товар найден
        """
        items = self.find_elements(self.ITEM_TITLE)
        for item in items:
            if title.lower() in item.text.lower():
                return True
        return False
