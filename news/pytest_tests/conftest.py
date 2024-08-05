# news/tests/conftest.py
import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from news.forms import BAD_WORDS
from news.models import Comment, News

User = get_user_model()


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def user():
    return User.objects.create(username='Мимо Крокодил')


@pytest.fixture
def auth_client(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def unauth_client():
    return Client()


@pytest.fixture
def form_data():
    return {'text': 'Текст комментария'}


@pytest.fixture
def bad_words_data():
    return {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}


@pytest.fixture
def comment(news, user):
    return Comment.objects.create(
        news=news,
        author=user,
        text='Текст комментария'
    )


@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def create_data(db):
    news = News.objects.create(title='Заголовок', text='Текст')
    author = User.objects.create(username='Лев Толстой')
    reader = User.objects.create(username='Читатель простой')
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return {
        'news': news,
        'author': author,
        'reader': reader,
        'comment': comment
    }
