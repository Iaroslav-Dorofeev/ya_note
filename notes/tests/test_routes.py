from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """
    Тестирование маршрутов.

    В этом блоке тестов проверяется работоспособность маршрутов с учетом
    прав доступа авторизованных и неавторизованных пользователей.
    """
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Читатель')
        cls.note = Note.objects.create(
            title='Название заметки',
            text=('Текст заметки'),
            slug='routes',
            author=cls.author
        )
        cls.URLS_FOR_ANONYMOUS = (
            ('notes:home', None),
            ('users:login', None),
            ('users:logout', None),
            ('users:signup', None),
        )
        cls.URLS_ONLY_FOR_AUTHOR = (
            ('notes:detail', (cls.note.slug,)),
            ('notes:edit', (cls.note.slug,)),
            ('notes:delete', (cls.note.slug,)),
        )
        cls.URLS_FOR_AUTH_USER = (
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )

    def test_pages_availability_for_anonymous_user(self):
        for name, args in self.URLS_FOR_ANONYMOUS:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pyges_availability_for_auth_user(self):
        for name, args in self.URLS_FOR_AUTH_USER:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                self.client.force_login(self.reader)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_different_users(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name, args in self.URLS_ONLY_FOR_AUTHOR:
                with self.subTest(name=name):
                    url = reverse(name, args=args)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        for name, args in (self.URLS_ONLY_FOR_AUTHOR
                           + self.URLS_FOR_AUTH_USER):
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
