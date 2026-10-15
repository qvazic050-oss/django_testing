from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNoteCreation(TestCase):
    """Тестирование создания заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создать пользователя и подготовить данные для заметки."""
        cls.url = reverse('notes:add')
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': 'Текст',
            'title': 'Заголовок',
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверить, что анонимный пользователь не создаёт заметку."""
        self.client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Проверить создание заметки авторизованным пользователем."""
        self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)

        note = Note.objects.get()
        self.assertEqual(note.text, 'Текст')
        self.assertEqual(note.title, 'Заголовок')
        self.assertEqual(note.author, self.user)

    def test_two_identical_slug(self):
        """Проверить, что нельзя создать заметки с одинаковым slug."""
        self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)

        self.auth_client.post(self.url, data=self.form_data)
        self.assertEqual(Note.objects.count(), 1)

    def test_automatic_creation_slug(self):
        """Проверить автоматическое создание slug из заголовка."""
        self.auth_client.post(self.url, data=self.form_data)

        note = Note.objects.get()
        self.assertEqual(note.slug, 'zagolovok')


class TestNoteEditDelete(TestCase):
    """Тестирование редактирования и удаления заметок."""

    @classmethod
    def setUpTestData(cls):
        """Создать автора, читателя и заметку для тестов."""
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)

        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)

        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )

        cls.note_url = reverse('notes:success')
        cls.edit_url = reverse(
            'notes:edit',
            args=(cls.note.slug,)
        )
        cls.delete_url = reverse(
            'notes:delete',
            args=(cls.note.slug,)
        )
        cls.form_data = {
            'text': 'Изменённый текст',
            'title': 'Изменённый заголовок',
        }

    def test_author_can_delete_note(self):
        """Проверить, что автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)

        self.assertRedirects(response, self.note_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        """Проверить запрет удаления чужой заметки."""
        response = self.reader_client.delete(self.delete_url)

        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Проверить, что автор может редактировать свою заметку."""
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data
        )

        self.assertRedirects(response, self.note_url)

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, 'Изменённый текст')
        self.assertEqual(self.note.title, 'Изменённый заголовок')

    def test_user_cant_edit_note_of_another_user(self):
        """Проверить запрет редактирования чужой заметки."""
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data
        )

        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND
        )

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, 'Текст')
        self.assertEqual(self.note.title, 'Заголовок')
