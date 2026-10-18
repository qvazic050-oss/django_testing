
"""Тесты содержимого страниц заметок."""

from .common_test import NOTES_URL, BaseTestCase


class TestNotesContent(BaseTestCase):
    """Тестирование содержимого страниц со списком заметок."""

    def test_author_sees_own_notes(self):
        """Проверить, что автор видит свои заметки."""
        response = self.client.get(NOTES_URL)

        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']

        self.assertEqual(object_list.count(), 1)
        self.assertEqual(object_list.first().author, self.author)

    def test_reader_does_not_see_author_notes(self):
        """Проверить, что читатель не видит чужие заметки."""
        self.login_as_reader()
        response = self.client.get(NOTES_URL)

        self.assertIn('object_list', response.context)
        self.assertEqual(
            response.context['object_list'].count(),
            0,
        )
