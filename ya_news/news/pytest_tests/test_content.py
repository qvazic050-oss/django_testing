"""Тесты содержимого страниц новостей."""

from django.urls import reverse

from news.forms import CommentForm


def test_home_page(client, news_10):
    """Проверить ограничение количества новостей на главной странице."""
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']

    assert len(news_10) == 11
    assert len(object_list) == 10


def test_news_order(client, news_10):
    """Проверить сортировку новостей от новых к старым."""
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']

    all_dates = [news.date for news in object_list]
    assert all_dates == sorted(all_dates, reverse=True)


def test_detail_page_contains_form(author_client, news):
    """Проверить наличие формы комментария у автора."""
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)

    assert isinstance(response.context['form'], CommentForm)


def test_detail_page_contains_form_for_user(client, news):
    """Проверить отсутствие формы у анонимного пользователя."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)

    assert 'form' not in response.context


def test_comments_order(client, news, comments):
    """Проверить сортировку комментариев от старых к новым."""
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)

    news_from_context = response.context['news']
    all_comments = news_from_context.comment_set.all()
    all_dates = [comment.created for comment in all_comments]

    assert all_dates == sorted(all_dates)
