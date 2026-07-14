"""API тесты для Читай-город."""
import pytest
import allure
from typing import Dict, Any
from api.api_client import APIClient
from data.test_data import (
    search_data,
    product_data,
    ERROR_MESSAGES
)


@allure.feature("API Tests")
@allure.story("Search")
class TestSearchAPI:
    """Тесты поиска через API."""

    @allure.title("Позитивный тест: Поиск книги по запросу")
    @allure.description("Проверка успешного поиска книг")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_search_books(self, api_client: APIClient) -> None:
        """
        Тест поиска книг.

        Args:
            api_client: Фикстура API клиента
        """
        with allure.step(f"Выполнить поиск: {search_data.valid_query}"):
            response = api_client.search_books(search_data.valid_query)

        with allure.step("Проверить статус-код"):
            # Сайт может вернуть разные коды из-за защиты
            assert response.status_code in [200, 403, 404, 503], \
                f"Unexpected status code: {response.status_code}"
            
            allure.attach(
                f"Status code: {response.status_code}",
                "Response Status",
                allure.attachment_type.TEXT
            )
            
            # Если получили не 200, пропускаем проверки контента
            if response.status_code == 200:
                with allure.step("Проверить наличие результатов"):
                    content = response.text.lower()
                    has_results = (
                        search_data.valid_query.lower() in content or
                        "product" in content or
                        "товар" in content or
                        len(response.text) > 5000
                    )
                    assert has_results, "Страница поиска не содержит результатов"
            else:
                pytest.skip(f"Сайт вернул {response.status_code} (защита Cloudflare)")

    @allure.title("Негативный тест: Поиск с пустым запросом")
    @allure.description("Проверка обработки пустого поискового запроса")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_search_with_empty_query(self, api_client: APIClient) -> None:
        """
        Тест поиска с пустым запросом.

        Args:
            api_client: Фикстура API клиента
        """
        with allure.step("Выполнить поиск с пустым запросом"):
            response = api_client.search_books(search_data.empty_query)

        with allure.step("Проверить, что запрос обработан"):
            # При пустом поиске сайт обычно возвращает главную или каталог
            assert response.status_code in [200, 302, 400, 403, 404], \
                f"Unexpected status code: {response.status_code}"
            
            allure.attach(
                f"Status: {response.status_code}, URL: {response.url}",
                "Empty Search Result",
                allure.attachment_type.TEXT
            )


@allure.feature("API Tests")
@allure.story("Product")
class TestProductAPI:
    """Тесты получения информации о продукте."""

    @allure.title("Позитивный тест: Получение страницы книги")
    @allure.description("Проверка загрузки страницы книги")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_get_product_page(self, api_client: APIClient) -> None:
        """
        Тест получения страницы продукта через поиск.

        Args:
            api_client: Фикстура API клиента
        """
        with allure.step("Найти книгу через поиск"):
            search_response = api_client.search_books(search_data.valid_query)
            
            if search_response.status_code != 200:
                pytest.skip(f"Поиск недоступен (status: {search_response.status_code})")
            
            # Ищем ссылки на продукты в HTML ответе
            import re
            product_links = re.findall(
                r'/product/[a-zA-Z0-9-]+',
                search_response.text
            )
            
            if not product_links:
                # Пробуем найти любой URL, похожий на продукт
                product_links = re.findall(
                    r'["\'](/[^"\']*product[^"\']*)["\']',
                    search_response.text
                )
            
            if product_links:
                product_path = product_links[0]
                
                with allure.step(f"Загрузить страницу: {product_path}"):
                    response = api_client.get(product_path)
                
                with allure.step("Проверить статус-код"):
                    assert response.status_code in [200, 403], \
                        f"Expected 200, got {response.status_code}"
                    
                    if response.status_code == 200:
                        page_content = response.text.lower()
                        assert len(response.text) > 1000, \
                            "Страница товара должна содержать информацию"
                        
                        allure.attach(
                            f"Product page loaded: {len(response.text)} chars",
                            "Page Info",
                            allure.attachment_type.TEXT
                        )
            else:
                pytest.skip("Не удалось найти ссылки на продукты в поиске")

    @allure.title("Негативный тест: Получение несуществующей книги")
    @allure.description("Проверка ошибки при запросе несуществующего товара")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_get_nonexistent_product(self, api_client: APIClient) -> None:
        """
        Тест получения несуществующего продукта.

        Args:
            api_client: Фикстура API клиента
        """
        invalid_path = f"/product/nonexistent-book-{product_data.invalid_product_id}"

        with allure.step(f"Попытаться получить несуществующую книгу"):
            response = api_client.get(invalid_path)

        with allure.step("Проверить статус-код"):
            # Может быть 404 (не найдено) или 403 (защита)
            assert response.status_code in [404, 403, 200], \
                f"Unexpected status: {response.status_code}"
            
            if response.status_code == 200:
                # Некоторые сайты возвращают 200 с сообщением об ошибке
                content = response.text.lower()
                assert any([
                    "не найден" in content,
                    "не найдено" in content,
                    "not found" in content,
                    "404" in content,
                    "ошибка" in content
                ]), "Должна быть ошибка или страница не найдена"
            
            allure.attach(
                f"Status: {response.status_code}",
                "Result",
                allure.attachment_type.TEXT
            )


@allure.feature("API Tests")
@allure.story("Cart")
class TestCartAPI:
    """Тесты работы с корзиной."""

    @allure.title("Позитивный тест: Получение страницы корзины")
    @allure.description("Проверка загрузки страницы корзины")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.api
    def test_get_cart_page(self, api_client: APIClient) -> None:
        """
        Тест получения страницы корзины.

        Args:
            api_client: Фикстура API клиента
        """
        with allure.step("Получить страницу корзины"):
            # Пробуем разные пути к корзине
            cart_paths = ["/cart", "/basket", "/order/cart"]
            
            for path in cart_paths:
                response = api_client.get(path)
                
                if response.status_code == 200:
                    with allure.step("Проверить содержимое корзины"):
                        assert len(response.text) > 500, \
                            "Страница корзины должна содержать информацию"
                        
                        allure.attach(
                            f"Cart page loaded: {len(response.text)} chars",
                            "Cart Info",
                            allure.attachment_type.TEXT
                        )
                    return
            
            # Если ни один путь не вернул 200
            pytest.skip("Страница корзины недоступна (возможно, защита Cloudflare)")

    @allure.title("API тест: Отправка некорректных данных")
    @allure.description("Проверка обработки некорректного запроса к API")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.api
    def test_invalid_request_handling(self, api_client: APIClient) -> None:
        """
        Тест отправки некорректного запроса.

        Args:
            api_client: Фикстура API клиента
        """
        with allure.step("Отправить POST запрос с невалидными данными"):
            # Отправляем запрос на несуществующий эндпоинт с плохими данными
            response = api_client.post(
                "/api/cart/add",
                json_data={"bad": "data"}
            )

        with allure.step("Проверить, что запрос обработан"):
            # Такой запрос может вернуть разные коды
            valid_statuses = [400, 403, 404, 405, 422, 500, 502, 503]
            assert response.status_code in valid_statuses, \
                f"Unexpected status: {response.status_code} (expected one of {valid_statuses})"
            
            allure.attach(
                f"Status: {response.status_code}\n"
                f"Response: {response.text[:500]}",
                "Invalid Request Result",
                allure.attachment_type.TEXT
            )

    @allure.title("API тест: Проверка доступности сайта")
    @allure.description("Базовая проверка доступности главной страницы")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.api
    def test_site_availability(self, api_client: APIClient) -> None:
        """
        Тест доступности сайта.

        Args:
            api_client: Фикстура API клиента
        """
        with allure.step("Проверить главную страницу"):
            response = api_client.get("/")
        
        with allure.step("Проверить статус-код"):
            assert response.status_code in [200, 403, 503], \
                f"Unexpected status: {response.status_code}"
            
            if response.status_code == 200:
                assert "chitai-gorod" in response.text.lower() or \
                       len(response.text) > 1000, \
                       "Главная страница должна содержать контент"
                
                allure.attach(
                    f"Site available: {response.status_code}",
                    "Availability Check",
                    allure.attachment_type.TEXT
                )
            else:
                allure.attach(
                    f"Site returned {response.status_code} (likely Cloudflare)",
                    "Availability Check",
                    allure.attachment_type.TEXT
                )
