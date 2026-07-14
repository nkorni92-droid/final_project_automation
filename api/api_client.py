"""API клиент для работы с Читай-город."""
from typing import Dict, Any, Optional
import requests
import allure
import json
from config.settings import Settings


class APIClient:
    """Клиент для работы с API."""

    def __init__(self) -> None:
        """Инициализация API клиента."""
        self.base_url = Settings.BASE_URL
        self.session = requests.Session()
        self.session.headers.update(Settings.get_headers())
        
        # Добавляем cookies для обхода базовой защиты
        self.session.cookies.set("cookie_policy", "1")
        self.session.cookies.set("city_id", "1")

    @allure.step("GET запрос к {endpoint}")
    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Выполнить GET запрос.

        Args:
            endpoint: Эндпоинт API
            params: Параметры запроса
            headers: Заголовки запроса

        Returns:
            requests.Response: Ответ сервера
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.get(
                url,
                params=params,
                headers=request_headers,
                timeout=10
            )
            
            allure.attach(
                f"Status: {response.status_code}\nURL: {response.url}",
                "Response Info",
                allure.attachment_type.TEXT
            )
            
            return response
        except requests.RequestException as e:
            allure.attach(str(e), "Request Error", allure.attachment_type.TEXT)
            raise

    @allure.step("POST запрос к {endpoint}")
    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> requests.Response:
        """
        Выполнить POST запрос.

        Args:
            endpoint: Эндпоинт API
            data: Данные формы
            json_data: JSON данные
            headers: Заголовки запроса

        Returns:
            requests.Response: Ответ сервера
        """
        url = f"{self.base_url}{endpoint}"
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=10
            )
            
            allure.attach(
                f"Status: {response.status_code}\nURL: {response.url}",
                "Response Info",
                allure.attachment_type.TEXT
            )
            
            return response
        except requests.RequestException as e:
            allure.attach(str(e), "Request Error", allure.attachment_type.TEXT)
            raise

    @allure.step("Поиск книг по запросу '{query}'")
    def search_books(self, query: str) -> requests.Response:
        """
        Поиск книг по запросу через API поиска сайта.

        Args:
            query: Поисковый запрос

        Returns:
            requests.Response: Ответ с результатами поиска
        """
        # Используем реальный эндпоинт поиска Читай-город
        return self.get(
            "/search",
            params={"q": query, "suggest": "1"}
        )

    @allure.step("Получить страницу книги {product_slug}")
    def get_product_page(self, product_slug: str) -> requests.Response:
        """
        Получить страницу книги по slug.

        Args:
            product_slug: Slug продукта

        Returns:
            requests.Response: Ответ со страницей книги
        """
        return self.get(f"/product/{product_slug}")

    @allure.step("Добавить книгу в корзину")
    def add_to_cart(
        self,
        product_id: int,
        quantity: int = 1
    ) -> requests.Response:
        """
        Добавить книгу в корзину.

        Args:
            product_id: ID продукта
            quantity: Количество

        Returns:
            requests.Response: Ответ сервера
        """
        return self.post(
            "/cart/add",
            json_data={
                "productId": product_id,
                "quantity": quantity
            }
        )

    @allure.step("Получить содержимое корзины")
    def get_cart(self) -> requests.Response:
        """
        Получить содержимое корзины.

        Returns:
            requests.Response: Ответ с содержимым корзины
        """
        return self.get("/cart")
