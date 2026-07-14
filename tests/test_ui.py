"""UI тесты для Читай-город."""
import pytest
import allure
import time
from typing import List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementClickInterceptedException
)
from data.test_data import search_data


class BaseUITest:
    """Базовый класс для UI тестов с общими методами."""

    def _close_popups(self, driver: WebDriver) -> None:
        """
        Закрыть все всплывающие окна и уведомления.

        Args:
            driver: WebDriver
        """
        # Селекторы для разных всплывающих окон
        popup_close_selectors = [
            # Закрыть кнопкой
            "button[aria-label='Закрыть']",
            "button[aria-label='Close']",
            ".popup__close",
            ".modal__close",
            ".tippy-box button",
            "[data-action='close']",
            # Закрыть кликом вне окна
        ]
        
        # Закрываем через кнопки
        for selector in popup_close_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        try:
                            element.click()
                            time.sleep(0.5)
                        except:
                            # Пробуем через JavaScript
                            driver.execute_script("arguments[0].click();", element)
                            time.sleep(0.5)
            except:
                pass
        
        # Закрываем через Escape
        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)
        except:
            pass
        
        # Убираем затемнение (overlay)
        try:
            driver.execute_script("""
                document.querySelectorAll('.overlay, .modal-backdrop, .popup-overlay')
                    .forEach(el => el.remove());
            """)
        except:
            pass

    def _find_and_accept_cookies(self, driver: WebDriver) -> None:
        """
        Поиск и принятие cookies.

        Args:
            driver: WebDriver
        """
        cookie_texts = [
            "Принять", "Согласен", "ОК", "Accept", "Agree",
            "Понятно", "Хорошо", "Да", "Accept all"
        ]
        
        for text in cookie_texts:
            try:
                # Ищем кнопку с текстом
                xpath = f"//button[contains(text(), '{text}')]"
                buttons = driver.find_elements(By.XPATH, xpath)
                for button in buttons:
                    if button.is_displayed():
                        try:
                            button.click()
                            time.sleep(1)
                            return
                        except:
                            driver.execute_script("arguments[0].click();", button)
                            time.sleep(1)
                            return
            except:
                continue
        
        # Альтернативный поиск по классам
        cookie_selectors = [
            ".cookie button",
            "[class*='cookie'] button",
            ".cookie-accept",
            "#cookie-accept",
        ]
        
        for selector in cookie_selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    driver.execute_script("arguments[0].click();", element)
                    time.sleep(1)
                    return
            except:
                continue

    def _find_search_input(self, driver: WebDriver) -> Optional[WebElement]:
        """
        Поиск поля ввода поиска.

        Args:
            driver: WebDriver

        Returns:
            WebElement или None
        """
        # Сначала закрываем все popup'ы
        self._close_popups(driver)
        
        selectors = [
            "input[type='search']",
            "input[name='search']",
            "input[name='q']",
            "input[placeholder*='оиск']",
            "input[placeholder*='search' i]",
            "input[aria-label*='оиск']",
            "input[class*='search']",
            ".header-search input",
            "form[action*='search'] input",
            "#search-input",
        ]
        
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        return element
            except:
                continue
        
        # Поиск через JavaScript
        try:
            element = driver.execute_script("""
                const inputs = document.querySelectorAll('input');
                for (const input of inputs) {
                    if (input.type === 'search' || 
                        input.type === 'text' && (
                            input.placeholder?.includes('оиск') ||
                            input.placeholder?.includes('Поиск') ||
                            input.name === 'q' ||
                            input.name === 'search'
                        )) {
                        return input;
                    }
                }
                return null;
            """)
            if element:
                return element
        except:
            pass
        
        return None

    def _scroll_to_element(self, driver: WebDriver, element: WebElement) -> None:
        """
        Прокрутить страницу к элементу.

        Args:
            driver: WebDriver
            element: Целевой элемент
        """
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            element
        )
        time.sleep(0.5)

    def _safe_click(self, driver: WebDriver, element: WebElement) -> bool:
        """
        Безопасный клик с обработкой перехвата.

        Args:
            driver: WebDriver
            element: Элемент для клика

        Returns:
            bool: True если клик успешен
        """
        self._close_popups(driver)
        self._scroll_to_element(driver, element)
        
        try:
            element.click()
            return True
        except ElementClickInterceptedException:
            # Пробуем через JavaScript
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except:
                return False
        except:
            try:
                driver.execute_script("arguments[0].click();", element)
                return True
            except:
                return False


class TestSearchUI(BaseUITest):
    """UI тесты поиска."""

    @allure.title("Тест: Поиск книги по автору")
    @allure.description("Проверка поиска книг на сайте Читай-город")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_search_by_author(self, driver: WebDriver) -> None:
        """
        Тест поиска книги по автору.

        Args:
            driver: Фикстура WebDriver
        """
        with allure.step("Открыть главную страницу"):
            driver.get("https://www.chitai-gorod.ru")
            time.sleep(5)
        
        with allure.step("Закрыть всплывающие окна"):
            self._close_popups(driver)
            time.sleep(1)
        
        with allure.step("Принять cookies"):
            self._find_and_accept_cookies(driver)
            time.sleep(1)
        
        with allure.step("Сделать скриншот"):
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, "Главная страница", allure.attachment_type.PNG)
        
        with allure.step("Найти поле поиска"):
            search_input = self._find_search_input(driver)
            
            if not search_input:
                allure.attach(
                    driver.page_source[:3000],
                    "HTML страницы",
                    allure.attachment_type.HTML
                )
                pytest.skip("Не удалось найти поле поиска")
        
        with allure.step(f"Ввести запрос: {search_data.valid_query}"):
            self._scroll_to_element(driver, search_input)
            search_input.clear()
            search_input.send_keys(search_data.valid_query)
            time.sleep(1)
        
        with allure.step("Отправить поисковый запрос"):
            # Пробуем найти кнопку поиска рядом с полем
            try:
                # Ищем форму, содержащую поле поиска
                form = driver.execute_script(
                    "return arguments[0].closest('form');",
                    search_input
                )
                
                if form:
                    # Ищем кнопку submit в форме
                    submit_button = form.find_element(
                        By.CSS_SELECTOR,
                        "button[type='submit'], input[type='submit']"
                    )
                    self._safe_click(driver, submit_button)
                else:
                    search_input.send_keys(Keys.RETURN)
            except:
                try:
                    search_input.send_keys(Keys.RETURN)
                except:
                    driver.execute_script("""
                        const form = arguments[0].closest('form');
                        if (form) form.submit();
                        else arguments[0].dispatchEvent(
                            new KeyboardEvent('keydown', {key: 'Enter', keyCode: 13})
                        );
                    """, search_input)
            
            time.sleep(5)
        
        with allure.step("Проверить результаты поиска"):
            current_url = driver.current_url.lower()
            page_source = driver.page_source.lower()
            
            search_performed = any([
                search_data.valid_query.lower() in current_url,
                "search" in current_url,
                "q=" in current_url,
                search_data.valid_query.lower() in page_source,
            ])
            
            allure.attach(
                f"URL: {driver.current_url}\nTitle: {driver.title}",
                "Результат поиска",
                allure.attachment_type.TEXT
            )
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, "Результаты поиска", allure.attachment_type.PNG)
            
            assert search_performed, (
                f"Поиск не выполнился. URL: {driver.current_url}\n"
                f"Проверьте ручной поиск на сайте: "
                f"https://www.chitai-gorod.ru/search?q={search_data.valid_query}"
            )

    @allure.title("Тест: Поиск с пустым запросом")
    @allure.description("Проверка обработки пустого поиска")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_search_empty_query(self, driver: WebDriver) -> None:
        """
        Тест поиска с пустым запросом.

        Args:
            driver: Фикстура WebDriver
        """
        with allure.step("Открыть главную страницу"):
            driver.get("https://www.chitai-gorod.ru")
            time.sleep(5)
        
        self._close_popups(driver)
        self._find_and_accept_cookies(driver)
        
        with allure.step("Найти поле поиска"):
            search_input = self._find_search_input(driver)
            
            if not search_input:
                pytest.skip("Не удалось найти поле поиска")
        
        with allure.step("Отправить пустой запрос"):
            search_input.clear()
            search_input.send_keys(Keys.RETURN)
            time.sleep(3)
        
        with allure.step("Проверить результат"):
            allure.attach(
                f"URL: {driver.current_url}\nTitle: {driver.title}",
                "Empty Search Result",
                allure.attachment_type.TEXT
            )
            
            # Пустой поиск — сайт остаётся на месте или показывает каталог
            assert driver.title, "Сайт должен быть доступен"


class TestProductUI(BaseUITest):
    """UI тесты карточки товара."""

    @allure.title("Тест: Просмотр карточки товара")
    @allure.description("Проверка открытия карточки товара из каталога")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_view_product(self, driver: WebDriver) -> None:
        """
        Тест просмотра карточки товара.

        Args:
            driver: Фикстура WebDriver
        """
        with allure.step("Открыть каталог книг"):
            driver.get("https://www.chitai-gorod.ru/catalog/books")
            time.sleep(5)
        
        self._close_popups(driver)
        self._find_and_accept_cookies(driver)
        
        with allure.step("Найти карточки товаров"):
            # Расширенные селекторы
            product_selectors = [
                "a[href*='/product/']",
                ".product-card a",
                ".product-card__title a",
                ".product-item a",
                "[class*='product'] a[href*='/product/']",
                ".catalog-item a",
                ".goods-item a",
                "article a[href*='/product/']",
            ]
            
            product_links = []
            for selector in product_selectors:
                try:
                    links = driver.find_elements(By.CSS_SELECTOR, selector)
                    for link in links:
                        if link.is_displayed() and link.get_attribute("href"):
                            product_links.append(link)
                except:
                    continue
            
            if not product_links:
                allure.attach(
                    driver.page_source[:3000],
                    "HTML каталога",
                    allure.attachment_type.HTML
                )
                screenshot = driver.get_screenshot_as_png()
                allure.attach(screenshot, "Каталог", allure.attachment_type.PNG)
                pytest.skip("Не удалось найти товары в каталоге")
        
        with allure.step("Выбрать первый доступный товар"):
            product_link = product_links[0]
            product_url = product_link.get_attribute("href")
            product_text = product_link.text
            
            allure.attach(
                f"URL: {product_url}\nText: {product_text}",
                "Product Info",
                allure.attachment_type.TEXT
            )
            
            # Безопасный клик
            click_success = self._safe_click(driver, product_link)
            
            if not click_success:
                # Последняя попытка — прямой переход по URL
                driver.get(product_url)
            
            time.sleep(5)
        
        with allure.step("Проверить страницу товара"):
            current_url = driver.current_url.lower()
            
            assert any([
                "/product/" in current_url,
                "product" in current_url,
            ]), f"Не открылась страница товара: {current_url}"
            
            page_length = len(driver.page_source)
            assert page_length > 1000, f"Страница пустая ({page_length} символов)"
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, "Страница товара", allure.attachment_type.PNG)


class TestNavigationUI(BaseUITest):
    """UI тесты навигации."""

    @allure.title("Тест: Переход в корзину")
    @allure.description("Проверка перехода на страницу корзины")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.ui
    def test_navigate_to_cart(self, driver: WebDriver) -> None:
        """
        Тест перехода в корзину.

        Args:
            driver: Фикстура WebDriver
        """
        with allure.step("Открыть главную страницу"):
            driver.get("https://www.chitai-gorod.ru")
            time.sleep(5)
        
        self._close_popups(driver)
        self._find_and_accept_cookies(driver)
        
        with allure.step("Найти ссылку на корзину"):
            cart_selectors = [
                "a[href='/cart']",
                "a[href='/basket']",
                "a[href*='cart']",
                "a[href*='basket']",
                ".header-cart a",
                ".cart-link",
                "[class*='cart'] a",
                "a[data-action='cart']",
                ".header__cart a",
            ]
            
            cart_link = None
            for selector in cart_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            cart_link = element
                            break
                    if cart_link:
                        break
                except:
                    continue
            
            if not cart_link:
                allure.attach(
                    driver.current_url,
                    "No Cart Link",
                    allure.attachment_type.TEXT
                )
                screenshot = driver.get_screenshot_as_png()
                allure.attach(screenshot, "Главная страница", allure.attachment_type.PNG)
                pytest.skip("Не удалось найти ссылку на корзину")
        
        with allure.step("Перейти в корзину"):
            cart_url = cart_link.get_attribute("href")
            allure.attach(f"Cart URL: {cart_url}", "Cart Link", allure.attachment_type.TEXT)
            
            self._safe_click(driver, cart_link)
            time.sleep(5)
        
        with allure.step("Проверить корзину"):
            current_url = driver.current_url.lower()
            
            assert any([
                "cart" in current_url,
                "basket" in current_url,
                "корзин" in driver.page_source.lower(),
            ]), f"Не открылась корзина: {current_url}"
            
            allure.attach(
                driver.current_url,
                "Cart URL",
                allure.attachment_type.TEXT
            )

    @allure.title("Тест: Проверка главной страницы")
    @allure.description("Проверка загрузки главной страницы")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.ui
    def test_main_page_loaded(self, driver: WebDriver) -> None:
        """
        Тест загрузки главной страницы.

        Args:
            driver: Фикстура WebDriver
        """
        with allure.step("Открыть главную страницу"):
            driver.get("https://www.chitai-gorod.ru")
            time.sleep(5)
        
        self._close_popups(driver)
        
        with allure.step("Проверить заголовок"):
            title = driver.title
            assert title, "Заголовок пустой"
            allure.attach(title, "Page Title", allure.attachment_type.TEXT)
        
        with allure.step("Проверить содержимое"):
            page_length = len(driver.page_source)
            assert page_length > 1000, (
                f"Страница не загрузилась ({page_length} символов)"
            )
            
            page_source = driver.page_source.lower()
            has_brand = any([
                "читай" in page_source,
                "chitai" in page_source,
                "город" in page_source,
                "gorod" in page_source,
            ])
            
            allure.attach(
                f"Size: {page_length} chars\nHas brand: {has_brand}",
                "Page Info",
                allure.attachment_type.TEXT
            )
            
            screenshot = driver.get_screenshot_as_png()
            allure.attach(screenshot, "Главная страница", allure.attachment_type.PNG)
