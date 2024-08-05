# news/tests/test_logic.py
from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(news, unauth_client, form_data):
    url = reverse('news:detail', args=(news.id,))
    unauth_client.post(url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_can_create_comment(news, auth_client, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = auth_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == f'{url}#comments'
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    user_id = auth_client.session['_auth_user_id']
    assert comment.author.id == int(user_id)


@pytest.mark.django_db
def test_user_cant_use_bad_words(news, auth_client, bad_words_data):
    url = reverse('news:detail', args=(news.id,))
    response = auth_client.post(url, data=bad_words_data)
    assert response.status_code == HTTPStatus.OK
    assert response.context['form'].errors['text'] == [WARNING]
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_delete_comment(news, comment, auth_client, delete_url):
    response = auth_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == (
        f'{reverse("news:detail", args=(news.id,))}#comments'
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_user_cant_delete_comment_of_another_user(
    news,
    comment,
    unauth_client,
    delete_url
):
    response = unauth_client.delete(delete_url)
    assert response.status_code == HTTPStatus.FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_author_can_edit_comment(news, comment, auth_client, edit_url):
    form_data = {'text': 'Обновлённый комментарий'}
    response = auth_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    assert response.url == (
        f'{reverse("news:detail", args=(news.id,))}#comments'
    )
    comment.refresh_from_db()
    assert comment.text == form_data['text']


@pytest.mark.django_db
def test_user_cant_edit_comment_of_another_user(
    news,
    comment,
    unauth_client,
    edit_url
):
    form_data = {'text': 'Обновлённый комментарий'}
    response = unauth_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'
