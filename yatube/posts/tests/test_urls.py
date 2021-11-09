from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.models import Group, Post

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
        self.user = User.objects.get(username='test_name')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_not_author_client = Client()
        self.authorized_not_author_client.force_login(self.not_author)

    # Проверяется общедоступные страницы
    def test_homepage_index(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_about_author(self):
        """Страница /about/author/ доступна любому пользователю."""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, 200)

    def test_about_tech(self):
        """Страница /about/tech/ доступна любому пользователю."""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, 200)

    def test_group_slug(self):
        """Страница /group/<slug>/ доступна любому пользователю."""
        response = self.guest_client.get('/group/test_slug/')
        self.assertEqual(response.status_code, 200)

    def test_profile_username(self):
        """Страница /profile/<username>/ доступна любому пользователю."""
        response = self.guest_client.get('/profile/test_name/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_id(self):
        """Страница /posts/<post_id>/ доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{PostURLTests.post.pk}/')
        self.assertEqual(response.status_code, 200)

    def test_404_unexisting_page(self):
        """Сервер возвращает код 404, если страница не найдена"""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    # Проверяется доступность страниц для авторизованного пользователя
    def test_post_create(self):
        """Страница /post_create/ доступна авторизованному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

    def test_posts_post_id_edit(self):
        """Страница /posts/<post_id>/edit/ доступна только автору поста."""
        response = self.authorized_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, 200)

    # Проверяется редирект если не автор поста
    def test_post_id_edit_not_author(self):
        """Страница /posts/<post_id>/edit/ перенаправляет пользователя
        на страницу /post_detail/ если не автор поста.
        """
        response = self.authorized_not_author_client.get(
            f'/posts/{PostURLTests.post.pk}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{PostURLTests.post.pk}/')

    # Проверяется вызываемые шаблоны для каждого адреса
    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/test_slug/',
            'posts/profile.html': '/profile/test_name/',
            'posts/post_detail.html': f'/posts/{PostURLTests.post.pk}/',
            'posts/create_post.html': '/create/',
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/'
        }
        for template, url in templates_url_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
