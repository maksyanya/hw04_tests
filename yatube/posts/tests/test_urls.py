from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls.base import reverse

from posts.models import Group
from posts.models import Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_name')
        cls.not_author = User.objects.create_user(
            username='test_not_author'
        )
        cls.group = Group.objects.create(slug='test_slug')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый текст',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.authorized_not_author_client = Client()
        self.authorized_not_author_client.force_login(self.not_author)

    # Проверяется общедоступные страницы
    def all_url_not_authorized_user(self):
        '''Проверяется по списку урлы общедоступных страниц.'''
        url_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', args=[self.group.slug]),
            reverse('posts:profile', args=[self.post.pk]),
            reverse('posts:post_detail', args=[self.post.pk])
        ]
        for url in url_list:
            response = self.guest_client.get(url)
            self.assertEqual(response.status_code, 200)

    def test_404_unexisting_page(self):
        """Сервер возвращает код 404, если страница не найдена"""
        response = self.guest_client.get('unexisting_page')
        self.assertEqual(response.status_code, 404)

    # Проверяется доступность страниц для авторизованного пользователя
    def all_url_authorized_user(self):
        '''Проверяется по списку урлы авторизованным пользователям.'''
        url_list = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', args=[self.post.pk]),
        ]
        for url in url_list:
            response = self.authorized_client.get(url)
            self.assertEqual(response.status_code, 200)

    # Проверяется редирект если не автор поста
    def test_post_id_edit_not_author(self):
        """Страница /posts/<post_id>/edit/ перенаправляет пользователя
        на страницу /post_detail/ если не автор поста.
        """
        response = self.authorized_not_author_client.get(reverse(
            'posts:post_edit',
            args=[self.post.pk]), follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail',
            args=[self.post.pk]))

    # Проверяется вызываемые шаблоны для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/profile.html': '/profile/test_name/',
            'posts/post_detail.html': f'/posts/{PostURLTests.post.pk}/',
            'posts/create_post.html': '/create/',
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    template)
