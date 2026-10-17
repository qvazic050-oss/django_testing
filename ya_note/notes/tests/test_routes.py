from http import HTTPStatus

from notes.models import Note

from .common_test import (
    ADD_URL,
    LIST_URL,
    SUCCESS_URL,
    BaseTestCase,
    get_note_url,
)


class TestNotesRoutes(BaseTestCase):
    """Тестирование доступности страниц заметок."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

    def test_pages_available_for_author(self):
        """Проверить доступность страниц автору заметки."""
        urls = (
            (get_note_url('notes:edit', self.note), HTTPStatus.OK),
            (get_note_url('notes:delete', self.note), HTTPStatus.OK),
            (get_note_url('notes:detail', self.note), HTTPStatus.OK),
            (LIST_URL, HTTPStatus.OK),
            (SUCCESS_URL, HTTPStatus.OK),
            (ADD_URL, HTTPStatus.OK),
        )

        for url, status in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, status)
