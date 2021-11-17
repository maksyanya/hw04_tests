from django.test import Client
from django.test import TestCase
from django.urls import reverse

from django import forms
from posts.models import Group
from posts.models import Post
from posts.models import User

USERNAME = 'test_author'
TITLE = 'test_group'
SLUG = 'test_slug'
DESCRIPTION = 'test_description'
TITLE_NEW = 'test_group_new'
SLUG_NEW = 'test_slug_new'
DESCRIPTION_NEW = 'test_description_new'

PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
POST_CREATE_URL = reverse('posts:post_create')


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
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.editor = User.objects.create_user(username='User')
        self.editor_client = Client()
        self.editor_client.force_login(self.editor)

    def test_form_create(self):
        '''Проверяется создания нового поста авторизированным пользователем.'''
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'test_text',
        }
        response = self.authorized_client.post(POST_CREATE_URL,
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, PROFILE_URL)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.post.refresh_from_db()
        self.assertEqual(self.group.id, form_data['group'])
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.text, form_data['text'])

    def test_edit_post(self):
        '''Проверяется редактирование поста через форму на странице.'''
        form_data_new = {'text': 'edited_text', 'group': self.group_new.id}
        response = self.authorized_client.post(self.POST_EDIT_URL,
                                               data=form_data_new,
                                               follow=True)
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.post.refresh_from_db()
        self.assertEqual(self.group_new.id, form_data_new['group'])
        self.assertEqual(self.post.text, form_data_new['text'])
        self.assertEqual(self.post.author, self.user)

    def test_post_create_and_edit_page_show_correct_context(self):
        '''Проверяется добавление/редактирование записи
        с правильным контекстом.'''
        self.url_list = [POST_CREATE_URL, self.POST_EDIT_URL]
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
