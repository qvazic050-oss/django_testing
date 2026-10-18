
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse, reverse_lazy

from notes.models import Note


User = get_user_model()

HOME_URL = reverse_lazy('notes:home')
LOGIN_URL = reverse_lazy('users:login')
SIGNUP_URL = reverse_lazy('users:signup')
LOGOUT_URL = reverse_lazy('users:logout')

NOTES_URL = reverse_lazy('notes:list')
LIST_URL = NOTES_URL
ADD_URL = reverse_lazy('notes:add')
SUCCESS_URL = reverse_lazy('notes:success')

DETAIL_URL = reverse_lazy(
    'notes:detail',
    kwargs={'slug': 'common-note'},
)
EDIT_URL = reverse_lazy(
    'notes:edit',
    kwargs={'slug': 'common-note'},
)
DELETE_URL = reverse_lazy(
    'notes:delete',
    kwargs={'slug': 'common-note'},
)


class BaseTestCase(TestCase):
    """Общие данные и авторизация для тестов приложения notes."""

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(
            username='Лев Толстой',
        )
        cls.reader = User.objects.create_user(
            username='Читатель простой',
        )
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author,
            slug='common-note',
        )

    def setUp(self):
        self.client.force_login(self.author)

        self.author_client = self.client

        self.reader_client = Client()
        self.reader_client.force_login(self.reader)

    def login_as_reader(self):
        """Авторизовать основной клиент как читателя."""
        self.client.force_login(self.reader)

    def login_as_author(self):
        """Авторизовать основной клиент как автора."""
        self.client.force_login(self.author)


def get_note_url(name, note):
    """Получить URL заметки по имени маршрута и объекту заметки."""
    return reverse(name, kwargs={'slug': note.slug})
