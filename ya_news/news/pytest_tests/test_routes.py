
"""Тесты доступности страниц и прав пользователей."""

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'url_fixture',
    (
        'comment_delete_url',
        'comment_edit_url',
    ),
)
def test_redirects_anonymous_user_to_login(
    client,
    login_url,
    request,
    url_fixture,
):
    """Проверить перенаправление анонимного пользователя на вход."""
    url = request.getfixturevalue(url_fixture)
    expected_url = f'{login_url}?next={url}'

    response = client.get(url)

    assertRedirects(response, expected_url)


def test_pages_availability_and_user_permissions(
    client,
    author_client,
    reader_client,
    home_url,
    login_url,
    signup_url,
    news_detail_url,
    comment_edit_url,
    comment_delete_url,
    logout_url,
    subtests,
):
    """Проверить доступность страниц и права пользователей."""
    public_urls = (
        home_url,
        login_url,
        signup_url,
        news_detail_url,
    )

    public_clients = (
        ('anonymous', client),
        ('author', author_client),
        ('reader', reader_client),
    )

    for user_name, test_client in public_clients:
        for url in public_urls:
            with subtests.test(user=user_name, url=url):
                response = test_client.get(url)
                assert response.status_code == HTTPStatus.OK

    comment_urls = (
        comment_edit_url,
        comment_delete_url,
    )

    for url in comment_urls:
        with subtests.test(user='author', url=url):
            response = author_client.get(url)
            assert response.status_code == HTTPStatus.OK

    for url in comment_urls:
        with subtests.test(user='reader', url=url):
            response = reader_client.get(url)
            assert response.status_code == HTTPStatus.NOT_FOUND

    with subtests.test(user='author', url=logout_url):
        response = author_client.post(logout_url)
        assert response.status_code == HTTPStatus.OK
        assert '_auth_user_id' not in author_client.session
