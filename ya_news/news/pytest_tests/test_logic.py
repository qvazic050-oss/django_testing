"""Тесты логики работы с комментариями."""

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects

from news.models import Comment

from .constants import COMMENT_FORM_DATA


def test_user_can_create_comment(
    author_client,
    author,
    news,
    news_detail_url,
):
    """Проверить создание комментария авторизованным пользователем."""
    comment_pks_before = set(
        Comment.objects.values_list('pk', flat=True)
    )

    response = author_client.post(
        news_detail_url,
        data=COMMENT_FORM_DATA,
    )

    assertRedirects(
        response,
        f'{news_detail_url}#comments',
    )

    new_comment = Comment.objects.exclude(
        pk__in=comment_pks_before
    ).get()

    assert new_comment.text == COMMENT_FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(
    client,
    news_detail_url,
    login_url,
):
    """Проверить запрет создания комментария анонимным пользователем."""
    comments_count = Comment.objects.count()

    response = client.post(
        news_detail_url,
        data=COMMENT_FORM_DATA,
    )

    expected_url = f'{login_url}?next={news_detail_url}'

    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comments_count


def test_user_cant_use_bad_words(
    author_client,
    news_detail_url,
):
    """Проверить запрет комментариев со стоп-словами."""
    comments_count = Comment.objects.count()
    bad_words_form_data = COMMENT_FORM_DATA.copy()
    bad_words_form_data['text'] = 'редиска текст'

    response = author_client.post(
        news_detail_url,
        data=bad_words_form_data,
    )

    assertFormError(
        response.context['form'],
        'text',
        'Не ругайтесь!',
    )
    assert Comment.objects.count() == comments_count


def test_author_can_delete_comment(
    author_client,
    comment,
    news_comments_url,
    comment_delete_url,
):
    """Проверить удаление своего комментария."""
    comments_count = Comment.objects.count()

    response = author_client.delete(comment_delete_url)

    assertRedirects(response, news_comments_url)
    assert Comment.objects.count() == comments_count - 1
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_author_can_edit_comment(
    author_client,
    comment,
    news_comments_url,
    comment_edit_url,
):
    """Проверить редактирование своего комментария."""
    original_author = comment.author
    original_news = comment.news
    comments_count = Comment.objects.count()

    response = author_client.post(
        comment_edit_url,
        data=COMMENT_FORM_DATA,
    )

    assertRedirects(response, news_comments_url)
    assert Comment.objects.count() == comments_count

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert updated_comment.text == COMMENT_FORM_DATA['text']
    assert updated_comment.author == original_author
    assert updated_comment.news == original_news


@pytest.mark.parametrize('action', ('delete', 'edit'))
def test_user_cant_change_comment_of_another_user(
    reader_client,
    comment,
    comment_action_urls,
    action,
):
    """Проверить запрет изменения чужого комментария."""
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news
    comments_count = Comment.objects.count()
    url = comment_action_urls[action]

    response = (
        reader_client.delete(url)
        if action == 'delete'
        else reader_client.post(url, data=COMMENT_FORM_DATA)
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == comments_count

    unchanged_comment = Comment.objects.get(pk=comment.pk)
    assert unchanged_comment.text == original_text
    assert unchanged_comment.author == original_author
    assert unchanged_comment.news == original_news
