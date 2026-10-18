from notes.forms import NoteForm

from .common_test import (
    ADD_URL,
    BaseTestCase,
    get_note_url,
)


class TestAddAndEditPage(BaseTestCase):
    """Тестирование форм создания и редактирования заметок."""

    def test_form_is_present(self):
        """Проверить наличие формы создания и редактирования."""
        urls = (
            get_note_url('notes:edit', self.note),
            ADD_URL,
        )

        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(
                    response.context['form'],
                    NoteForm,
                )
