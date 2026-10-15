"""Фикстуры для тестов новостного приложения."""

from datetime import timedelta

import pytest
from django.conf import settings
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
def reader_client(reader, client, db):
    """Создать клиент авторизованного читателя."""
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
def author_client(author, client, db):
    """Создать клиент автора."""
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
    return News.objects.bulk_create(all_news)


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
def id_news_for_args(news):
    """Вернуть ID новости для аргументов URL."""
    return (news.id,)


@pytest.fixture
def id_comment_for_args(comment):
    """Вернуть ID комментария для аргументов URL."""
    return (comment.id,)


@pytest.fixture
def form_data():
    """Подготовить данные формы комментария."""
    return {
        'text': 'Новый текст',
    }
