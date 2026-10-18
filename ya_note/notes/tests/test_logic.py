
"""Тесты логики создания, редактирования и удаления заметок."""

from http import HTTPStatus

from notes.models import Note

from .common_test import (
    ADD_URL,
    LOGIN_URL,
    SUCCESS_URL,
    BaseTestCase,
    get_note_url,
)


class TestNoteCreation(BaseTestCase):
    """Тестирование создания заметок."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.form_data = {
            'title': 'Новая заметка',
            'text': 'Новый текст',
        }

    def test_anonymous_user_cant_create_note(self):
        """Проверить запрет создания заметки анонимным пользователем."""
        notes_before = Note.objects.count()
        self.client.logout()

        response = self.client.post(
            ADD_URL,
            data=self.form_data,
        )

        self.assertRedirects(
            response,
            f'{LOGIN_URL}?next={ADD_URL}',
        )
        self.assertEqual(Note.objects.count(), notes_before)

    def test_user_can_create_note(self):
        """Проверить создание заметки авторизованным пользователем."""
        notes_before = Note.objects.count()
        existing_ids = set(
            Note.objects.values_list('pk', flat=True)
        )

        response = self.client.post(
            ADD_URL,
            data=self.form_data,
        )

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)

        new_notes = Note.objects.exclude(pk__in=existing_ids)
        self.assertEqual(new_notes.count(), 1)

        note = new_notes.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.author)

    def test_two_identical_slug(self):
        """Проверить запрет создания заметки с существующим slug."""
        form_data = {
            'title': 'Другая заметка',
            'text': 'Другой текст',
            'slug': self.note.slug,
        }
        notes_before = Note.objects.count()

        response = self.client.post(
            ADD_URL,
            data=form_data,
        )

        self.assertEqual(
            response.status_code,
            HTTPStatus.OK,
        )
        self.assertIn('form', response.context)
        self.assertIn(
            'slug',
            response.context['form'].errors,
        )
        self.assertEqual(Note.objects.count(), notes_before)
        self.assertTrue(
            Note.objects.filter(pk=self.note.pk).exists()
        )

    def test_automatic_creation_slug(self):
        """Проверить автоматическое создание slug из заголовка."""
        form_data = {
            'title': 'Automatic Slug',
            'text': 'Текст заметки',
        }
        notes_before = Note.objects.count()
        existing_ids = set(
            Note.objects.values_list('pk', flat=True)
        )

        response = self.client.post(
            ADD_URL,
            data=form_data,
        )

        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), notes_before + 1)

        new_notes = Note.objects.exclude(pk__in=existing_ids)
        self.assertEqual(new_notes.count(), 1)

        note = new_notes.get()
        self.assertEqual(note.slug, 'automatic-slug')
        self.assertEqual(note.title, form_data['title'])
        self.assertEqual(note.text, form_data['text'])
        self.assertEqual(note.author, self.author)


class TestNoteEditDelete(BaseTestCase):
    """Тестирование редактирования и удаления заметок."""

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.original_note_fields = {
            'title': cls.note.title,
            'text': cls.note.text,
            'author_id': cls.note.author_id,
            'slug': cls.note.slug,
        }
        cls.note_url = SUCCESS_URL
        cls.edit_url = get_note_url('notes:edit', cls.note)
        cls.delete_url = get_note_url('notes:delete', cls.note)
        cls.form_data = {
            'text': 'Изменённый текст',
            'title': 'Изменённый заголовок',
        }

    def assert_note_unchanged(self):
        """Проверить, что заметка сохранила исходные поля."""
        note = Note.objects.get(pk=self.note.pk)
        for field, value in self.original_note_fields.items():
            with self.subTest(field=field):
                self.assertEqual(getattr(note, field), value)

    def test_author_can_edit_note(self):
        """Проверить, что автор может редактировать свою заметку."""
        notes_before = Note.objects.count()

        response = self.client.post(
            self.edit_url,
            data=self.form_data,
        )
        self.assertRedirects(response, self.note_url)

        note = Note.objects.get(pk=self.note.pk)

        self.assertEqual(Note.objects.count(), notes_before)
        self.assertIn('text', self.form_data)
        self.assertIn('title', self.form_data)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверить запрет редактирования чужой заметки."""
        notes_before = Note.objects.count()
        self.login_as_reader()

        response = self.client.post(
            self.edit_url,
            data=self.form_data,
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
        )

        self.assertEqual(Note.objects.count(), notes_before)
        self.assert_note_unchanged()

    def test_author_can_delete_note(self):
        """Проверить, что автор может удалить свою заметку."""
        notes_before = Note.objects.count()

        response = self.client.delete(self.delete_url)
        self.assertRedirects(response, self.note_url)

        self.assertEqual(Note.objects.count(), notes_before - 1)
        self.assertFalse(
            Note.objects.filter(pk=self.note.pk).exists()
        )

    def test_user_cant_delete_note_of_another_user(self):
        """Проверить запрет удаления чужой заметки."""
        notes_before = Note.objects.count()
        self.login_as_reader()

        response = self.client.delete(self.delete_url)
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
        )

        self.assertEqual(Note.objects.count(), notes_before)
        self.assertTrue(
            Note.objects.filter(pk=self.note.pk).exists()
        )
        self.assert_note_unchanged()
