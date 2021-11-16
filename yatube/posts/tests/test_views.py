import random
from django.test import Client
from django.test import TestCase

from posts.models import Group
from posts.models import Post
from posts.models import User
from posts.settings import POSTS_PER_PAGE


USERNAME = 'test_author'
TITLE = 'test_title'
SLUG = 'test_slug'
DESCRIPTION = 'test_discription'
POST_ID = '1'
TEXT = 'test_text'
TITLE_ANOTHER = 'another_title'
SLUG_ANOTHER = 'another_slug'
DESCRIPTION_OTHER = 'other_description'

INDEX = '/'
GROUP_POSTS = f'/group/{SLUG}/'
PROFILE = f'/profile/{USERNAME}/'
POST_DETAIL = f'/posts/{POST_ID}/'
ANOTHER_GROUP = f'/group/{SLUG_ANOTHER}/'


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
        cls.url_list = [
            INDEX,
            GROUP_POSTS,
            PROFILE,
            POST_DETAIL
        ]

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_show_correct_context(self):
        '''Проверяется контекст шаблонов на соответствие.'''
        for url in self.url_list:
            response = self.authorized_client.get(url)
            if 'page_obj' in response.context and len(
                response.context['page_obj']
            ) == 1:
                post = response.context['page_obj'][0]
            else:
                post = response.context['post']
            self.assertEqual(post.group, self.post.group)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.text, self.post.text)

    def test_post_not_in_another_group(self):
        '''Проверяется, что пост не отображается в другой группе'''
        response_group = self.authorized_client.get(ANOTHER_GROUP)
        self.assertNotIn(self.post, response_group.context.get('page_obj'))

    def test_author_in_profile_page(self):
        '''Проверяется, что автор на станице профиля.'''
        response_author = self.authorized_client.get(PROFILE)
        self.assertEqual(self.author, response_author.context.get('author'))

    def test_group_in_group_posts_page_(self):
        '''Проверяется, что "группа" на странице групп-ленты..'''
        response_group = self.authorized_client.get(GROUP_POSTS)
        group_test = response_group.context.get('group')
        self.assertEqual(group_test, self.group)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_author')
        cls.group = Group.objects.create(title='test_title',
                                         slug='test_slug',
                                         description='test_discription')
        cls.add_pages = random.randint(1, POSTS_PER_PAGE - 1)
        cls.posts = (Post(author=cls.author,
                          group=cls.group,
                          text='test_post',
                          ) for i in range(
                              POSTS_PER_PAGE + cls.add_pages))
        cls.post = Post.objects.bulk_create(cls.posts)

        cls.url_list = [
            INDEX,
            GROUP_POSTS,
            PROFILE
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
                self.add_pages
            )
