from django.test import TestCase
from django.urls import reverse

from posts.forms import Post
from posts.models import Group
from posts.models import User

USERNAME = 'test_author'
SLUG = 'test_slug'
TEXT = 'test_text'


class PostRoutesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username=USERNAME)
        cls.group = Group.objects.create(slug=SLUG)
        cls.post = Post.objects.create(author=cls.user,
                                       group=cls.group,
                                       text=TEXT,
                                       )

    def test_urls_correct_use(self):
        '''Проверяется маршруты явных и рассчётных урлов.'''
        self.url_list = [
            [
                '/', reverse('posts:index')
            ],
            [
                '/create/', reverse('posts:post_create')
            ],
            [
                f'/group/{self.group.slug}/',
                reverse('posts:group_posts', args=[self.group.slug])
            ],
            [
                f'/posts/{self.post.id}/',
                reverse('posts:post_detail', args=[self.post.id])
            ],
            [
                f'/profile/{self.user.username}/',
                reverse('posts:profile', args=[self.user.username])
            ],
            [
                f'/posts/{self.post.id}/edit/',
                reverse('posts:post_edit', args=[self.post.id])
            ]
        ]
        for url, name in self.url_list:
            self.assertEqual(url, name)
