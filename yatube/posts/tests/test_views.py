from django.test import Client
from django.test import TestCase
from django.urls import reverse

from posts.models import Group
from posts.models import Post
from posts.models import User
from posts.settings import TEN_POSTS_PER_PAGE
from posts.settings import THREE_POSTS_PER_PAGE


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
        cls.url_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', args=[cls.group.slug]),
            reverse('posts:profile', args=[cls.author.username]),
            reverse('posts:post_detail', kwargs={'post_id': cls.post.pk})
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    # Проверяется, что в шаблон передан правильный контекст
    def test_templates_list_show_correct_context(self):
        '''Проверяется список шаблонов на соответствие контекста.'''
        for url in self.url_list:
            response = self.authorized_client.get(url)
            if 'page_obj' in response.context:
                post = response.context['page_obj'][0]
            else:
                post = response.context['post']
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.text, self.post.text)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_author')
        cls.group = Group.objects.create(title='test_title',
                                         slug='test_slug',
                                         description='test_discription')
        cls.posts = (Post(author=cls.author,
                          group=cls.group,
                          text='test_post',
                          ) for i in range(
                              TEN_POSTS_PER_PAGE + THREE_POSTS_PER_PAGE))
        cls.post = Post.objects.bulk_create(cls.posts)

        cls.url_list = [
            reverse('posts:index'),
            reverse('posts:group_posts', args=[cls.group.slug]),
            reverse('posts:profile', args=[cls.author.username])
        ]

    def setUp(self):
        self.guest_client = Client()

    def test_first_page_containse_ten_records(self):
        '''Проверяется отображение 10 постов на первой странице.'''
        for url in self.url_list:
            response = self.guest_client.get(url)
            self.assertEqual(len(
                response.context['page_obj']),
                TEN_POSTS_PER_PAGE
            )

    def test_second_page_containse_tree_records(self):
        '''Проверяется отображения 3 поста на первой странице.'''
        for url in self.url_list:
            response = self.guest_client.get(url + '?page=2')
            self.assertEqual(len(
                response.context['page_obj']),
                THREE_POSTS_PER_PAGE
            )
