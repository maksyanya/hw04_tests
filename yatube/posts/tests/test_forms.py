from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from django import forms
from posts.forms import PostForm
from posts.forms import Post
from posts.models import Group


User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_author')
        cls.group_old = Group.objects.create(
            title='test_group_old',
            slug='test_slug-old',
            description='test_description_old'
        )
        cls.group_new = Group.objects.create(
            title='test_group_new',
            slug='test_slug-new',
            description='test_description_new'
        )
        cls.post = Post.objects.create(author=cls.user,
                                       group=cls.group_old,
                                       text='test_text',
                                       )
        cls.author = User.objects.create_user(
            username='test_name',
            first_name='test_first_name',
            last_name='test_lats_name',
            email='test@test.ru'
        )

        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_form_create(self):
        """Проверяется создания нового поста авторизированным пользователем"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group_old.id,
            'text': 'test_new_text',
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='test_new_text',
            group=self.group_old.id).exists())

    def test_edit_post(self):
        """Проверяется редактирования поста через форму на странице."""
        form_data = {'text': 'test_edit_post', 'group': self.group_new.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.id]))
        self.assertTrue(Post.objects.filter(
            text='test_edit_post',
            group=self.group_new.id).exists())
        self.assertFalse(Post.objects.filter(
            text='test_edit_post',
            group=self.group_old.id).exists())

    def test_post_create_page_show_correct_context(self):
        '''Проверяется добавления записи с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_edit_page_show_correct_context(self):
        '''Проверяется редактирование записи с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)
