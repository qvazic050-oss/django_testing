
"""Фикстуры для тестов новостного приложения."""

from datetime import timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def reader(django_user_model, db):
    """Создать обычного пользователя."""
    return django_user_model.objects.create_user(
        username='Читатель',
        password='test-password',
    )


@pytest.fixture
def reader_client(reader):
    """Создать клиент авторизованного читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def author(django_user_model, db):
    """Создать автора комментария."""
    return django_user_model.objects.create_user(
        username='Автор',
        password='test-password',
    )


@pytest.fixture
def author_client(author):
    """Создать клиент автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def news(db):
    """Создать новость."""
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def news_10(db):
    """Создать 11 новостей для проверки ограничения на главной."""
    all_news = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(all_news)


@pytest.fixture
def comment(author, news, db):
    """Создать комментарий к новости."""
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
    )


@pytest.fixture
def comments(author, news, db):
    """Создать два комментария с разными датами."""
    all_comments = []

    for index in range(2):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Текст комментария {index}',
        )
        Comment.objects.filter(pk=comment.pk).update(
            created=timezone.now() + timedelta(days=index)
        )
        comment.refresh_from_db()
        all_comments.append(comment)

    return all_comments


@pytest.fixture
def home_url():
    """Вернуть URL главной страницы."""
    return reverse('news:home')


@pytest.fixture
def news_detail_url(news):
    """Вернуть URL страницы новости."""
    return reverse('news:detail', args=(news.pk,))


@pytest.fixture
def login_url():
    """Вернуть URL страницы входа."""
    return reverse('users:login')


@pytest.fixture
def signup_url():
    """Вернуть URL страницы регистрации."""
    return reverse('users:signup')


@pytest.fixture
def logout_url():
    """Вернуть URL выхода пользователя."""
    return reverse('users:logout')


@pytest.fixture
def news_comments_url(news_detail_url):
    """Вернуть URL страницы новости с якорем комментариев."""
    return f'{news_detail_url}#comments'


@pytest.fixture
def comment_edit_url(comment):
    """Вернуть URL редактирования комментария."""
    return reverse('news:edit', args=(comment.pk,))


@pytest.fixture
def comment_delete_url(comment):
    """Вернуть URL удаления комментария."""
    return reverse('news:delete', args=(comment.pk,))


@pytest.fixture
def comment_action_urls(comment_edit_url, comment_delete_url):
    """Вернуть URL редактирования и удаления комментария."""
    return {
        'edit': comment_edit_url,
        'delete': comment_delete_url,
    }


@pytest.fixture
def public_page_urls(home_url, login_url, signup_url):
    """Вернуть URL общедоступных страниц."""
    return {
        'главная': home_url,
        'вход': login_url,
        'регистрация': signup_url,
    }


@pytest.fixture
def comment_page_urls(comment_edit_url, comment_delete_url):
    """Вернуть URL страниц редактирования и удаления комментария."""
    return {
        'удаление': comment_delete_url,
        'редактирование': comment_edit_url,
    }
