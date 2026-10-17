
from http import HTTPStatus

from notes.models import Note

from .common_test import (
    SUCCESS_URL,
    BaseTestCase,
    get_note_url,
)


class TestNoteEditDelete(BaseTestCase):
    """Тестирование редактирования и удаления заметок."""
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
        )
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

    def test_author_can_edit_note(self):
        """Проверить, что автор может редактировать свою заметку."""
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data,
        )
        self.assertRedirects(response, self.note_url)

        note = Note.objects.get(pk=self.note.pk)
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(
            note.author_id,
            self.original_note_fields['author_id'],
        )

    def test_user_cant_edit_note_of_another_user(self):
        """Проверить запрет редактирования чужой заметки."""
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note = Note.objects.get(pk=self.note.pk)
        self.assert_note_fields_equal(
            note,
            self.original_note_fields,
        )

    def test_author_can_delete_note(self):
        """Проверить, что автор может удалить свою заметку."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.note_url)

        self.assertFalse(
            Note.objects.filter(pk=self.note.pk).exists()
        )

    def test_user_cant_delete_note_of_another_user(self):
        """Проверить запрет удаления чужой заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        note = Note.objects.get(pk=self.note.pk)
        self.assert_note_fields_equal(
            note,
            self.original_note_fields,
        )

    def test_author_can_delete_note(self):
        """Проверить, что автор может удалить свою заметку."""
        notes_before = set(
            Note.objects.values_list('pk', flat=True)
        )

        response = self.author_client.delete(self.delete_url)

        self.assertRedirects(response, self.note_url)

        notes_after = set(
            Note.objects.values_list('pk', flat=True)
        )
        self.assertEqual(
            notes_before - notes_after,
            {self.note.pk},
        )

    def test_user_cant_delete_note_of_another_user(self):
        """Проверить запрет удаления чужой заметки."""
        response = self.reader_client.delete(self.delete_url)

        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
        )
        self.assertTrue(
            Note.objects.filter(pk=self.note.pk).exists()
        )

    def test_author_can_edit_note(self):
        """Проверить, что автор может редактировать свою заметку."""
        response = self.author_client.post(
            self.edit_url,
            data=self.form_data,
        )

        self.assertRedirects(response, self.note_url)

        self.note.refresh_from_db()
        self.assertEqual(
            self.note.text,
            self.form_data['text'],
        )
        self.assertEqual(
            self.note.title,
            self.form_data['title'],
        )
        self.assertEqual(self.note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Проверить запрет редактирования чужой заметки."""
        response = self.reader_client.post(
            self.edit_url,
            data=self.form_data,
        )

        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
        )

        self.note.refresh_from_db()
        self.assertEqual(self.note.text, 'Текст')
        self.assertEqual(self.note.title, 'Заголовок')
        self.assertEqual(self.note.author, self.author)
