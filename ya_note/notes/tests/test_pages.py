
from notes.models import Note

from .common_test import (
    NOTES_URL,
    ADD_URL,
    BaseTestCase,
    get_note_url,
)


class TestNotesPage(BaseTestCase):
    """Тестирование списка заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создать заметки для тестов списка."""
        super().setUpTestData()

        all_notes = [
            Note(
                title=f'Новость{index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'note-{index}',
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_list(self):
        """Проверить наличие заметок автора в списке."""
        response = self.author_client.get(NOTES_URL)

        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']

        self.assertEqual(object_list.count(), 5)
        self.assertEqual(object_list[0].author, self.author)

    def test_reader_context_list(self):
        """Проверить отсутствие чужих заметок в списке читателя."""
        response = self.reader_client.get(NOTES_URL)

        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']

        self.assertEqual(object_list.count(), 0)

    def test_author_context_list(self):
        """Проверить количество заметок автора в списке."""
        response = self.author_client.get(NOTES_URL)

        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']

        self.assertEqual(object_list.count(), 5)


class TestAddAndEditPage(BaseTestCase):
    """Тестирование форм создания и редактирования заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создать заметку для тестов форм."""
        super().setUpTestData()

        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author,
        )

    def test_form(self):
        """Проверить наличие формы на страницах добавления и редактирования."""
        urls = (
            get_note_url('notes:edit', self.note),
            ADD_URL,
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
