from django.test import Client
from django.test import TestCase
from django.urls import reverse

from django import forms
from posts.forms import PostForm
from posts.forms import Post
from posts.models import Group
from posts.models import User

PROFILE = 'posts:profile'
POST_DETAIL = 'posts:post_detail'
POST_CREATE = 'posts:post_create'
POST_EDIT = 'posts:post_edit'
AUTH_LOGIN = 'login'


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_author')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description'
        )
        cls.group_new = Group.objects.create(
            title='test_group_new',
            slug='test_slug-new',
            description='test_description_new'
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

        self.url_profile = reverse(
            PROFILE,
            kwargs={'username': self.user.username})
        self.url_post_detail = reverse(
            POST_DETAIL,
            args=[self.post.id])
        self.url_post_create = reverse(
            POST_CREATE)
        self.url_post_edit = reverse(
            POST_EDIT,
            kwargs={'post_id': self.post.pk})

        self.url_list = [self.url_post_create, self.url_post_edit]

    def test_form_create(self):
        '''Проверяется создания нового поста авторизированным пользователем.'''
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'test_text',
        }
        response = self.authorized_client.post(self.url_post_create,
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, self.url_profile)
        self.assertEqual(Post.objects.count(), post_count + 1)
        Post.objects.filter(pk=self.post.pk).update(text=form_data['text'])
        self.post.refresh_from_db()
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.text, form_data['text'])

    def test_form_create_guest_client(self):
        '''Проверяется создания нового поста гостевым пользователем.'''
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'test_text',
        }
        response = self.client.post(self.url_post_create,
                                    data=form_data,
                                    follow=True)
        login = str(reverse(AUTH_LOGIN)) + '?next='
        self.assertRedirects(response, login + self.url_post_create)
        self.assertEqual(Post.objects.count(), post_count)

    def test_edit_post(self):
        '''Проверяется редактирование поста через форму на странице.'''
        form_data_new = {'text': 'edited_text', 'group': self.group_new.id}
        response = self.authorized_client.post(self.url_post_edit,
                                               data=form_data_new,
                                               follow=True)
        self.assertRedirects(response, self.url_post_detail)
        Post.objects.filter(pk=self.post.pk).update(
            group=self.group_new,
            text=form_data_new['text'])
        self.post.refresh_from_db()
        self.assertEqual(self.post.group, self.group_new)
        self.assertEqual(self.post.text, form_data_new['text'])

    def test_edit_post_other_user(self):
        '''Проверяется редактирование поста не автором.'''
        form_data = {
            'text': 'Отредактированный текст',
        }
        response = self.editor_client.post(self.url_post_edit,
                                           data=form_data,
                                           follow=True)
        self.assertRedirects(response, self.url_post_detail)

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
