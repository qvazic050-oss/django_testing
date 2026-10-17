
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse_lazy


User = get_user_model()

NOTES_URL = reverse_lazy('notes:list')
ADD_URL = reverse_lazy('notes:add')


class BaseTestCase(TestCase):
    """Общий предок для тестов приложения notes."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='Лев Толстой',
        )
        cls.reader = User.objects.create_user(
            username='Читатель',
        )

    def setUp(self):
        self.author_client = self.client_class()
        self.author_client.force_login(self.author)

        self.reader_client = self.client_class()
        self.reader_client.force_login(self.reader)


def get_note_url(name, note):
    """Получить URL заметки."""
    return reverse_lazy(name, args=(note.slug,))
