"""Тестовые данные."""
from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class TestUser:
    """Данные тестового пользователя."""
    email: str = "test@example.com"
    password: str = "TestPassword123!"
    name: str = "Тестовый Пользователь"


@dataclass
class SearchData:
    """Данные для поиска."""
    valid_query: str = "Пушкин"
    empty_query: str = ""
    expected_author: str = "Пушкин"
    expected_title: str = "Евгений Онегин"


@dataclass
class ProductData:
    """Данные о продуктах."""
    valid_product_id: int = 1
    invalid_product_id: int = 99999999
    expected_title: str = "книга"
    min_price: float = 100.0


@dataclass
class CartData:
    """Данные для корзины."""
    valid_quantity: int = 1
    invalid_quantity: int = -5
    invalid_product_id: str = "not_a_number"


# Экземпляры тестовых данных
test_user = TestUser()
search_data = SearchData()
product_data = ProductData()
cart_data = CartData()


# Ожидаемые сообщения об ошибках
ERROR_MESSAGES: Dict[str, str] = {
    "empty_query": "пустой",
    "not_found": "не найден",
    "validation_error": "VALIDATION_ERROR",
}
