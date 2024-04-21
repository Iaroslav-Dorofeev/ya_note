from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )
        cls.NOTE_IN_LIST = (
            (cls.author, True),
            (cls.reader, False),
        )
        cls.URL_PAGE_WITH_FORM = (
            ('notes:add', None),
            ('notes:edit', (cls.note.slug,))
        )

    def test_note_in_list_for_users(self):
        for user, note_in_list in self.NOTE_IN_LIST:
            with self.subTest(user=user, note_in_list=note_in_list):
                self.client.force_login(user)
                url = reverse('notes:list')
                response = self.client.get(url)
                object_list = response.context['object_list']
                result = self.note in object_list
                self.assertEqual(result, note_in_list)

    def test_create_and_edit_note_pages_contain_form(self):
        for name, slug in self.URL_PAGE_WITH_FORM:
            with self.subTest(name=name):
                self.client.force_login(self.author)
                url = reverse(name, args=slug)
                response = self.client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)
