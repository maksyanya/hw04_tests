from django.test import Client
from django.test import TestCase

from django import forms
from posts.forms import PostForm
from posts.forms import Post
from posts.models import Group
from posts.models import User

USERNAME = 'test_author'
POST_ID = '1'
TITLE = 'test_group'
SLUG = 'test_slug'
DESCRIPTION = 'test_description'
TITLE_NEW = 'test_group_new'
SLUG_NEW = 'test_slug_new'
DESCRIPTION_NEW = 'test_description_new'

PROFILE = f'/profile/{USERNAME}/'
POST_DETAIL = f'/posts/{POST_ID}/'
POST_CREATE = '/create/'
POST_EDIT = f'/posts/{POST_ID}/edit/'
LOGIN = '/auth/login/?next='


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION
        )
        cls.group_new = Group.objects.create(
            title=TITLE_NEW,
            slug=SLUG_NEW,
            description=DESCRIPTION_NEW
        )
        cls.post = Post.objects.create(author=cls.user,
                                       group=cls.group,
                                       text='test_text',
                                       )
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.editor = User.objects.create_user(username='User')
        self.editor_client = Client()
        self.editor_client.force_login(self.editor)
        self.url_list = [POST_CREATE, POST_EDIT]

    def test_form_create(self):
        '''Проверяется создания нового поста авторизированным пользователем.'''
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'test_text',
        }
        response = self.authorized_client.post(POST_CREATE,
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, PROFILE)
        self.assertEqual(Post.objects.count(), post_count + 1)

    def test_form_create_guest_client(self):
        '''Проверяется создания нового поста гостевым пользователем.'''
        form_data = {
            'group': self.group.id,
            'text': 'test_text',
        }
        response = self.client.post(POST_CREATE,
                                    data=form_data,
                                    follow=True)
        self.assertRedirects(response, LOGIN + POST_CREATE)

    def test_edit_post(self):
        '''Проверяется редактирование поста через форму на странице.'''
        form_data_new = {'text': 'edited_text', 'group': self.group_new.id}
        response = self.authorized_client.post(POST_EDIT,
                                               data=form_data_new,
                                               follow=True)
        self.assertRedirects(response, POST_DETAIL)
        self.post.refresh_from_db()
        self.assertEqual(self.post.group, self.group_new)
        self.assertEqual(self.post.text, form_data_new['text'])

    def test_post_create_and_edit_page_show_correct_context(self):
        '''Проверяется добавление/редактирование записи
        с правильным контекстом.'''
        for url in self.url_list:
            response = self.authorized_client.get(url)
            form_fields = {
                'group': forms.fields.ChoiceField,
                'text': forms.fields.CharField,
            }
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_fields = response.context['form'].fields[value]
                    self.assertIsInstance(form_fields, expected)
