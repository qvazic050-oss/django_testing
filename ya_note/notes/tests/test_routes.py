
"""Тесты доступности маршрутов приложения notes."""

from http import HTTPStatus

from .common_test import (
    ADD_URL,
    DELETE_URL,
    DETAIL_URL,
    EDIT_URL,
    HOME_URL,
    LIST_URL,
    LOGIN_URL,
    LOGOUT_URL,
    SIGNUP_URL,
    SUCCESS_URL,
    BaseTestCase,
)


class TestRoutes(BaseTestCase):
    """Тестирование доступности маршрутов."""

    def test_redirect_for_anonymous_client(self):
        """Проверить перенаправление анонимного пользователя."""
        self.client.logout()

        protected_urls = (
            ADD_URL,
            EDIT_URL,
            DELETE_URL,
            DETAIL_URL,
            LIST_URL,
            SUCCESS_URL,
        )

        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertRedirects(
                    response,
                    f'{LOGIN_URL}?next={url}',
                )

    def test_pages_available_for_users(self):
        """Проверить доступность маршрутов и права пользователей."""
        public_urls = (
            HOME_URL,
            LOGIN_URL,
            SIGNUP_URL,
        )

        users = (
            ('anonymous', None),
            ('author', self.author),
            ('reader', self.reader),
        )

        for user_name, user in users:
            if user is None:
                self.client.logout()
            else:
                self.client.force_login(user)

            for url in public_urls:
                with self.subTest(user=user_name, url=url):
                    response = self.client.get(url)
                    self.assertEqual(
                        response.status_code,
                        HTTPStatus.OK,
                    )

            with self.subTest(user=user_name, url=LOGOUT_URL):
                response = self.client.post(LOGOUT_URL)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                )

        self.login_as_author()

        author_urls = (
            LIST_URL,
            ADD_URL,
            SUCCESS_URL,
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
        )

        for url in author_urls:
            with self.subTest(user='author', url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                )

        self.login_as_reader()

        reader_urls = (
            DETAIL_URL,
            EDIT_URL,
            DELETE_URL,
        )

        for url in reader_urls:
            with self.subTest(user='reader', url=url):
                response = self.client.get(url)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.NOT_FOUND,
                )
