from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_author')
        cls.group = Group.objects.create(slug='test_slug')
        cls.post = Post.objects.create(author=cls.user,
                                       group=cls.group,
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
        self.user = User.objects.get(username='test_author')
        self.group = Group.objects.get()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.get(text='test_text')
        self.post_edit = Post.objects.create(author=self.user,
                                             group=self.group,
                                             text='updated_text')

    def test_form_create(self):
        """Проверяется создания нового поста авторизированным пользователем"""
        post_count = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Добавить',
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': 'test_author'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(Post.objects.filter(
            text='Добавить',
            group=self.group).exists())

    def test_edit_post(self):
        """Проверяется редактирования поста через форму на странице."""
        form_data = {'text': self.post_edit.text, 'group': self.group}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=[self.post.id]))
        self.assertEqual(Post.objects.filter(
            id=self.post.id).last().text, self.post_edit.text)
