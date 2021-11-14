from django.test import Client
from django.test import TestCase
from django.urls.base import reverse

from posts.models import Group
from posts.models import Post
from posts.models import User

INDEX = 'posts:index'
POST_EDIT = 'posts:post_edit'
GROUP_POSTS = 'posts:group_posts'
PROFILE = 'posts:profile'
POST_DETAIL = 'posts:post_detail'
UNEXIST_PAGE = '404'
POST_CREATE = 'posts:post_create'
POST_EDIT = 'posts:post_edit'
AUTH_LOGIN = 'login'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_name')
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

        self.cases = [[
            reverse(INDEX),
            self.guest_client,
            200
        ], [
            reverse(POST_EDIT, args=[self.post.pk]),
            self.authorized_client,
            200
        ], [
            reverse(GROUP_POSTS, args=[self.group.slug]),
            self.guest_client,
            200
        ], [
            reverse(PROFILE, args=[self.author.username]),
            self.guest_client,
            200
        ], [
            reverse(POST_DETAIL, args=[self.post.pk]), self.guest_client, 200
        ], [
            reverse(POST_CREATE),
            self.authorized_not_author_client,
            200
        ], [
            reverse(POST_EDIT, args=[self.post.pk]),
            self.authorized_client,
            200
        ]]
        self.urls = [
            self.cases[5][0],
            self.cases[6][0]
        ]

    # Проверяется все страницы авторизованных/неавторизованных пользователей
    def test_all_url_all_user(self):
        '''Проверяется по списку урлы всех страниц.'''
        for index in self.cases:
            response = index[1].get(index[0])
            self.assertEqual(response.status_code, index[2])

    # Проверяется редирект если не автор поста на станице редактирования
    def test_post_id_edit_not_author(self):
        '''Страница /posts/<post_id>/edit/ перенаправляет пользователя
        на страницу /post_detail/ если не автор поста.
        '''
        response = self.authorized_not_author_client.get(
            self.cases[1][0],
            follow=True)
        self.assertRedirects(response, self.cases[4][0])

    def test_redirect_anon_user_create_or_edit_post(self):
        '''
        Проверка редиректа анонимного пользователя, при обращении
        к странице создания/редактирования поста
        '''
        for url in self.urls:
            login = str(reverse(AUTH_LOGIN)) + '?next='
            response = self.guest_client.get(url, follow=True)
            self.assertRedirects(response, login + url)

    # Проверяется вызываемые шаблоны для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_posts',
                args=[self.group.slug]): 'posts/group_list.html',
            reverse(
                'posts:profile',
                args=[self.author.username]): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                args=[self.post.pk]): 'posts/create_post.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.authorized_client.get(url),
                    template)
