from django.test import Client
from django.test import TestCase
from django.urls import reverse

from posts.models import Group
from posts.models import Post
from posts.models import User

USERNAME = 'test_name'
NOT_AUTHOR = 'test_not_author'
SLUG = 'test_slug'
TEXT = 'test_text'

INDEX_URL = reverse('posts:index')
GROUP_POSTS_URL = reverse('posts:group_posts', kwargs={'slug': SLUG})
PROFILE_URL = reverse('posts:profile', kwargs={'username': USERNAME})
POST_CREATE_URL = reverse('posts:post_create')
UNEXIST_PAGE = '/404/'
LOGIN = reverse('login')


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username=USERNAME)
        cls.not_author = User.objects.create_user(
            username=NOT_AUTHOR
        )
        cls.group = Group.objects.create(slug=SLUG)
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text=TEXT,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.authorized_not_author_client = Client()
        self.authorized_not_author_client.force_login(self.not_author)

    # Проверяется все страницы авторизованных/неавторизованных пользователей
    def test_all_url_all_user(self):
        '''Проверяется по списку урлы всех страниц.'''
        cases = [
            [INDEX_URL, self.guest_client, 200],
            [GROUP_POSTS_URL, self.guest_client, 200],
            [PROFILE_URL, self.guest_client, 200],
            [self.POST_DETAIL_URL, self.guest_client, 200],
            [POST_CREATE_URL, self.authorized_not_author_client, 200],
            [self.POST_EDIT_URL, self.authorized_client, 200],
            [UNEXIST_PAGE, self.guest_client, 404],
            [POST_CREATE_URL, self.guest_client, 302],
            [self.POST_EDIT_URL, self.authorized_not_author_client, 302]
        ]
        for url, client, code in cases:
            with self.subTest(url=url):
                self.assertEqual(client.get(url).status_code, code)

    def test_redirect_urls_correct(self):
        '''Проверяется редирект страниц создания/редактирования поста.'''
        cases = [
            [self.POST_EDIT_URL,
             self.authorized_not_author_client,
             self.POST_DETAIL_URL],
            [POST_CREATE_URL,
             self.guest_client,
             LOGIN + '?next=' + POST_CREATE_URL],
            [self.POST_EDIT_URL,
             self.guest_client,
             LOGIN + '?next=' + self.POST_EDIT_URL]
        ]
        for url, client, finel_url in cases:
            with self.subTest(url=url):
                self.assertRedirects(client.get(url, follow=True), finel_url)

    # Проверяется вызываемые шаблоны для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX_URL: 'posts/index.html',
            GROUP_POSTS_URL: 'posts/group_list.html',
            PROFILE_URL: 'posts/profile.html',
            self.POST_DETAIL_URL: 'posts/post_detail.html',
            POST_CREATE_URL: 'posts/create_post.html',
            self.POST_EDIT_URL: 'posts/create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    template)
