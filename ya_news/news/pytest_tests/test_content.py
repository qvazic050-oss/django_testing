"""Тесты содержимого страниц новостей."""

from news.forms import CommentForm
from news.models import News


def test_home_page(client, home_url, news_10):
    """Проверить ограничение количества новостей на главной странице."""
    response = client.get(home_url)

    assert 'object_list' in response.context
    object_list = response.context['object_list']

    assert News.objects.count() == 11
    assert object_list.count() == 10


def test_news_order(client, home_url, news_10):
    """Проверить сортировку новостей от новых к старым."""
    response = client.get(home_url)

    assert 'object_list' in response.context
    object_list = response.context['object_list']

    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_detail_page_contains_form(
    author_client,
    news_detail_url,
):
    """Проверить наличие формы комментария у автора."""
    response = author_client.get(news_detail_url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)


def test_detail_page_contains_form_for_user(
    client,
    news_detail_url,
):
    """Проверить отсутствие формы у анонимного пользователя."""
    response = client.get(news_detail_url)

    assert 'form' not in response.context


def test_comments_order(client, news_detail_url, comments):
    """Проверить сортировку комментариев от старых к новым."""
    response = client.get(news_detail_url)

    assert 'news' in response.context
    news_from_context = response.context['news']
    all_comments = news_from_context.comment_set.all()
    all_dates = [comment.created for comment in all_comments]

    assert all_dates == sorted(all_dates)
