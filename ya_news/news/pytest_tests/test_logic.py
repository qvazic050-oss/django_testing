
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
    news_comments_url,
):
    """Проверить создание комментария авторизованным пользователем."""
    comments_before = set(
        Comment.objects.values_list('pk', flat=True)
    )

    response = author_client.post(
        news_detail_url,
        data=COMMENT_FORM_DATA,
    )

    assertRedirects(response, news_comments_url)

    comments_after = set(
        Comment.objects.values_list('pk', flat=True)
    )
    new_comment_ids = comments_after - comments_before

    assert len(new_comment_ids) == 1

    new_comment = Comment.objects.get(pk=new_comment_ids.pop())
    assert 'text' in COMMENT_FORM_DATA
    assert new_comment.text == COMMENT_FORM_DATA['text']
    assert new_comment.author == author
    assert new_comment.news == news


def test_anonymous_user_cant_create_comment(
    client,
    login_url,
    news_detail_url,
):
    """Проверить запрет создания комментария анонимным пользователем."""
    comments_before = set(
        Comment.objects.values_list('pk', flat=True)
    )

    response = client.post(
        news_detail_url,
        data=COMMENT_FORM_DATA,
    )

    expected_url = f'{login_url}?next={news_detail_url}'
    assertRedirects(response, expected_url)

    comments_after = set(
        Comment.objects.values_list('pk', flat=True)
    )
    assert comments_after == comments_before


def test_user_cant_use_bad_words(
    author_client,
    news_detail_url,
):
    """Проверить запрет комментариев со стоп-словами."""
    comments_before = set(
        Comment.objects.values_list('pk', flat=True)
    )
    bad_form_data = COMMENT_FORM_DATA.copy()
    bad_form_data['text'] = 'редиска текст'

    response = author_client.post(
        news_detail_url,
        data=bad_form_data,
    )

    assert 'form' in response.context
    assertFormError(
        response.context['form'],
        'text',
        'Не ругайтесь!',
    )

    comments_after = set(
        Comment.objects.values_list('pk', flat=True)
    )
    assert comments_after == comments_before


def test_author_can_delete_comment(
    author_client,
    comment,
    comment_delete_url,
    news_comments_url,
):
    """Проверить удаление своего комментария."""
    comments_before = set(
        Comment.objects.values_list('pk', flat=True)
    )

    response = author_client.delete(comment_delete_url)

    assertRedirects(response, news_comments_url)

    comments_after = set(
        Comment.objects.values_list('pk', flat=True)
    )
    assert comments_after == comments_before - {comment.pk}
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_author_can_edit_comment(
    author_client,
    comment,
    comment_edit_url,
    news_comments_url,
):
    """Проверить редактирование своего комментария."""
    original_author = comment.author
    original_news = comment.news
    comments_before = set(
        Comment.objects.values_list('pk', flat=True)
    )

    response = author_client.post(
        comment_edit_url,
        data=COMMENT_FORM_DATA,
    )

    assertRedirects(response, news_comments_url)

    comments_after = set(
        Comment.objects.values_list('pk', flat=True)
    )
    assert comments_after == comments_before

    updated_comment = Comment.objects.get(pk=comment.pk)
    assert 'text' in COMMENT_FORM_DATA
    assert updated_comment.text == COMMENT_FORM_DATA['text']
    assert updated_comment.author == original_author
    assert updated_comment.news == original_news


@pytest.mark.parametrize('action', ('delete', 'edit'))
def test_user_cant_change_comment_of_another_user(
    reader_client,
    comment,
    action,
    request,
):
    """Проверить запрет изменения чужого комментария."""
    original_text = comment.text
    original_author = comment.author
    original_news = comment.news
    comments_before = set(
        Comment.objects.values_list('pk', flat=True)
    )

    url = request.getfixturevalue(f'comment_{action}_url')

    if action == 'delete':
        response = reader_client.delete(url)
    else:
        response = reader_client.post(
            url,
            data=COMMENT_FORM_DATA,
        )

    assert response.status_code == HTTPStatus.NOT_FOUND

    comments_after = set(
        Comment.objects.values_list('pk', flat=True)
    )
    assert comments_after == comments_before

    unchanged_comment = Comment.objects.get(pk=comment.pk)
    assert unchanged_comment.text == original_text
    assert unchanged_comment.author == original_author
    assert unchanged_comment.news == original_news
