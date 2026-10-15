"""Тесты логики работы с комментариями."""

from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment


def test_user_can_create_comment(author_client, author, form_data, news):
    """Проверить создание комментария авторизованным пользователем."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))

    response = author_client.post(url, data=form_data)

    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == comments_count + 1

    new_comment = Comment.objects.latest('id')
    assert new_comment.text == form_data['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(client, form_data, news):
    """Проверить запрет создания комментария анонимным пользователем."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))

    response = client.post(url, data=form_data)

    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count


def test_user_cant_use_bad_words(author_client, news, form_data):
    """Проверить запрет комментариев со стоп-словами."""
    comments_count = Comment.objects.count()
    url = reverse('news:detail', args=(news.id,))
    form_data['text'] = 'редиска текст'

    response = author_client.post(url, data=form_data)

    assertFormError(
        response.context['form'],
        'text',
        'Не ругайтесь!',
    )
    assert Comment.objects.count() == comments_count


def test_author_can_delete_comment(author_client, news, comment):
    """Проверить удаление своего комментария."""
    comments_count = Comment.objects.count()
    url_to_comments = (
        reverse('news:detail', args=(news.id,)) + '#comments'
    )
    url = reverse('news:delete', args=(comment.id,))

    response = author_client.delete(url)

    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_author_can_edit_comment(author_client, news, form_data, comment):
    """Проверить редактирование своего комментария."""
    original_author = comment.author
    original_news = comment.news
    comments_count = Comment.objects.count()
    url_to_comments = (
        reverse('news:detail', args=(news.id,)) + '#comments'
    )
    url = reverse('news:edit', args=(comment.id,))

    response = author_client.post(url, data=form_data)

    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == comments_count

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == form_data['text']
    assert updated_comment.author == original_author
    assert updated_comment.news == original_news


@pytest.mark.parametrize('action', ('delete', 'edit'))
def test_user_cant_change_comment_of_another_user(
    reader_client,
    form_data,
    comment,
    action,
):
    """Проверить запрет изменения чужого комментария."""
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news
    comments_count = Comment.objects.count()
    url_name = 'news:' + action
    url = reverse(url_name, args=(comment.id,))

    if action == 'delete':
        response = reader_client.delete(url)
    else:
        response = reader_client.post(url, data=form_data)

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count

    unchanged_comment = Comment.objects.get(pk=comment.pk)
    assert unchanged_comment.text == original_text
    assert unchanged_comment.author == original_author
    assert unchanged_comment.news == original_news
