from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNotesPage(TestCase):
    """Тестирование списка заметок."""

    NOTES_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        """Создать пользователей и заметки для тестов."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.reader = User.objects.create(username='Читатель')
        all_notes = [
            Note(
                title=f'Новость{index}',
                text='Просто текст.',
                author=cls.author,
                slug=f'note-{index}'
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(all_notes)

    def test_notes_list(self):
        """Проверить наличие заметок автора в списке."""
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 5)
        self.assertEqual(object_list[0].author, self.author)

    def test_reader_context_list(self):
        """Проверить отсутствие чужих заметок в списке читателя."""
        self.client.force_login(self.reader)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 0)

    def test_author_context_list(self):
        """Проверить количество заметок автора в списке."""
        self.client.force_login(self.author)
        response = self.client.get(self.NOTES_URL)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 5)


class TestAddAndEditPage(TestCase):
    """Тестирование форм создания и редактирования заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создать автора и заметку для тестов."""
        cls.author = User.objects.create(username='Лев Толстой')
        cls.note = Note.objects.create(
            title='Тестовая заметка',
            text='Просто текст.',
            author=cls.author
        )

    def test_form(self):
        """Проверить наличие формы на страницах добавления и редактирования."""
        self.client.force_login(self.author)
        urls = (
            ('notes:edit', (self.note.slug,)),
            ('notes:add', None),
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertIn('form', response.context)
