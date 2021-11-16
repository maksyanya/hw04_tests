from django.test import Client
from django.test import TestCase

from posts.models import Group
from posts.models import Post
from posts.models import User

USERNAME = 'test_name'
NOT_AUTHOR = 'test_not_author'
SLUG = 'test_slug'
POST_ID = '1'
TEXT = 'test_text'

INDEX = '/'
GROUP_POSTS = f'/group/{SLUG}/'
POST_EDIT = 'posts:post_edit'
PROFILE = f'/profile/{USERNAME}/'
POST_DETAIL = f'/posts/{POST_ID}/'
POST_CREATE = '/create/'
POST_EDIT = f'/posts/{POST_ID}/edit/'
UNEXIST_PAGE = '/404/'
LOGIN = '/auth/login/?next='


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
            [INDEX, self.guest_client, 200],
            [GROUP_POSTS, self.guest_client, 200],
            [PROFILE, self.guest_client, 200],
            [POST_DETAIL, self.guest_client, 200],
            [POST_CREATE, self.authorized_not_author_client, 200],
            [POST_EDIT, self.authorized_client, 200],
            [UNEXIST_PAGE, self.guest_client, 404]
        ]
        for url, client, code in cases:
            response = client.get(url)
            self.assertEqual(response.status_code, code)

    def test_post_id_edit_not_author(self):
        '''Проверяется редирект страниц создания/редактирования поста.'''
        cases = [
            [POST_EDIT, self.authorized_not_author_client, POST_DETAIL],
            [POST_CREATE, self.guest_client, LOGIN + POST_CREATE],
            [POST_EDIT, self.guest_client, LOGIN + POST_EDIT],
        ]
        for url, client, finel_url in cases:
            response = client.get(url, follow=True)
            self.assertRedirects(response, finel_url)

    # Проверяется вызываемые шаблоны для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX: 'posts/index.html',
            GROUP_POSTS: 'posts/group_list.html',
            PROFILE: 'posts/profile.html',
            POST_DETAIL: 'posts/post_detail.html',
            POST_CREATE: 'posts/create_post.html',
            POST_EDIT: 'posts/create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    template)
