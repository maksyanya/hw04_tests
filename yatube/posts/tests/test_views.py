from django.test import Client
from django.test import TestCase
from django.urls import reverse

from posts.models import Group
from posts.models import Post
from posts.models import User
from posts.settings import POSTS_PER_PAGE


USERNAME = 'test_author'
TITLE = 'test_title'
SLUG = 'test_slug'
DESCRIPTION = 'test_discription'
TEXT = 'test_text'
TITLE_ANOTHER = 'another_title'
SLUG_ANOTHER = 'another_slug'
DESCRIPTION_OTHER = 'other_description'

INDEX_URL = reverse('posts:index')
GROUP_POSTS_URL = reverse('posts:group_posts', kwargs={'slug': SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
ANOTHER_GROUP = reverse('posts:group_posts', kwargs={'slug': SLUG_ANOTHER})


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(title=TITLE,
                                         slug=SLUG,
                                         description=DESCRIPTION)
        cls.another_group = Group.objects.create(title=TITLE_ANOTHER,
                                                 slug=SLUG_ANOTHER,
                                                 description=DESCRIPTION_OTHER)
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text=TEXT,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_show_correct_context(self):
        '''Проверяется контекст шаблонов на соответствие.'''
        url_list = [
            INDEX_URL,
            GROUP_POSTS_URL,
            PROFILE_URL,
            self.POST_DETAIL_URL
        ]
        for url in url_list:
            response = self.authorized_client.get(url)
            if 'page_obj' in response.context:
                post = response.context['page_obj'][0]
            else:
                post = response.context['post']
            self.assertEqual(Post.objects.count(), 1)
            self.assertEqual(post.group, self.post.group)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.text, self.post.text)

    def test_post_not_in_another_group(self):
        '''Проверяется, что пост не отображается в другой группе'''
        response_group = self.authorized_client.get(ANOTHER_GROUP)
        self.assertNotIn(self.post, response_group.context['page_obj'])

    def test_author_in_profile_page(self):
        '''Проверяется, что автор на станице профиля.'''
        response_author = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(self.author, response_author.context['author'])

    def test_group_in_group_posts_page_(self):
        '''Проверяется, что "группа" на странице групп-ленты..'''
        response = self.authorized_client.get(GROUP_POSTS_URL)
        group = response.context['group']
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.description, self.group.description)
        self.assertEqual(group.slug, self.group.slug)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_author')
        cls.group = Group.objects.create(title='test_title',
                                         slug='test_slug',
                                         description='test_discription')
        cls.posts = Post.objects.bulk_create(Post(author=cls.author,
                                                  group=cls.group,
                                                  text='test_post',
                                                  ) for i in range(
                                                      POSTS_PER_PAGE))
        cls.url_list = [
            INDEX_URL,
            GROUP_POSTS_URL,
            PROFILE_URL
        ]

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_of_first_page(self):
        '''Проверяется паджинатор вывода постов на первой странице.'''
        for url in self.url_list:
            response = self.guest_client.get(url)
            self.assertEqual(len(
                response.context['page_obj']),
                POSTS_PER_PAGE
            )

    def test_paginator_second_page(self):
        '''Проверяется паджинатор вывода постов на второй странице.'''
        for url in self.url_list:
            response = self.guest_client.get(url + '?page=2')
            self.assertEqual(len(
                response.context['page_obj']),
                POSTS_PER_PAGE
            )
