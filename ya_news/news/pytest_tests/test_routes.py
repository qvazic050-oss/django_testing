"""Тесты доступности страниц и прав пользователей."""

from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name',
    (
        'news:home',
        'users:login',
        'users:signup',
    ),
)
def test_pages_availability_for_anonymous_user(client, name, db):
    """Проверить доступность общедоступных страниц."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_news_detail_available_for_anonymous_user(client, news):
    """Проверить доступность страницы новости."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_pages_availability_for_author(author_client, name, comment):
    """Проверить доступ автора к своим комментариям."""
    url = reverse(name, args=(comment.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_pages_unavailable_for_another_user(
    reader_client, name, comment
):
    """Проверить запрет доступа к чужим комментариям."""
    url = reverse(name, args=(comment.id,))
    response = reader_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize('name', ('news:delete', 'news:edit'))
def test_redirects_anonymous_user_to_login(client, name, comment):
    """Проверить перенаправление анонимного пользователя на вход."""
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


def test_logout_by_post(author_client):
    """Проверить выход пользователя через POST-запрос."""
    author_client.post(reverse('users:logout'))
    assert '_auth_user_id' not in author_client.session
