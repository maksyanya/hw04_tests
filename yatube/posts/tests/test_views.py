from django.contrib.auth import get_user_model
from django.test import Client
from django.test import TestCase
from django.urls import reverse

from posts.models import Group
from posts.models import Post
from posts.settings import TEN_PAGE
from posts.settings import THREE_PAGE

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_author')
        cls.group = Group.objects.create(title='test_title',
                                         slug='test_slug',
                                         description='test_discription')
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='test_text',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    # Проверяется, что в шаблон передан правильный контекст
    def test_templates_list_show_correct_context(self):
        '''Проверяется список шаблонов на соответствие контекста.'''
        url_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', args=[self.group.slug]),
            reverse('posts:profile', args=[self.author.username]),
        ]
        for url in url_list:
            response = self.authorized_client.get(url)
            post = response.context['page_obj'][0]
            self.assertEqual(post.group, self.group)
            self.assertEqual(post.author, self.author)
            self.assertEqual(post.text, self.post.text)

    def test_post_detail_page_show_correct_context(self):
        '''Проверяется содержимое детализации поста.'''
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post_author = response.context.get('post').author
        post_text = response.context.get('post').text
        self.assertEqual(post_author, self.author)
        self.assertEqual(post_text, self.post.text)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_author')
        cls.group = Group.objects.create(title='test_title',
                                         slug='test_slug',
                                         description='test_discription')
        cls.templates = {
            1: reverse('posts:index'),
            2: reverse('posts:group_posts', args=[cls.group.slug]),
            3: reverse('posts:profile', args=[cls.author.username])
        }

        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.author,
                group=cls.group,
                text=f'test_post{i}',
            )

    def setUp(self):
        self.guest_client = Client()

    # Выполняется проверка количество постов для страниц
    def test_first_page_has_ten_posts(self):
        """Проверяется 10 постов на первой странице"""
        for i in self.templates.keys():
            with self.subTest(i=i):
                response = self.client.get(self.templates[i])
                self.assertEqual(len(response.context['page_obj']), TEN_PAGE)

    def test_second_page_has_three_posts(self):
        """Проверяется 3 поста на второй странице"""
        for i in self.templates.keys():
            with self.subTest(i=i):
                response = self.client.get(self.templates[i] + '?page=2')
                self.assertEqual(len(response.context['page_obj']), THREE_PAGE)
