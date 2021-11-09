from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

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
        self.user = User.objects.get()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Проверяется используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': (
                reverse('posts:group_posts', kwargs={'slug': 'test_slug'})
            ),
            'posts/profile.html': (
                reverse('posts:profile', kwargs={'username': 'test_author'})
            ),
            'posts/post_detail.html': (
                reverse('posts:post_detail', args=[PostPagesTests.post.id])
            ),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверяется, что в шаблон передан правильный контекст
    def test_index_page_show_correct_context(self):
        '''Проверяется шаблон index на соответствие контекста.'''
        response = self.guest_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_text_0, 'test_text')

    def test_group_post_page_show_correct_context(self):
        '''Проверяется шаблон group_list на соответствие контекста.'''
        response = self.guest_client.get(
            reverse('posts:group_posts', args=[self.group.slug])
        )
        first_object = response.context['page_obj'][0]
        post_group_0 = first_object.group
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_group_0, self.group)
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_text_0, 'test_text')

    def test_profile_page_show_correct_context(self):
        '''Проверяется шаблон profile на соответствие контекста.'''
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.author.username])
        )
        first_object = response.context['page_obj'][0]
        post_author_0 = first_object.author
        post_text_0 = first_object.text
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_text_0, 'test_text')

    def test_post_detail_page_show_correct_context(self):
        '''Проверяется содержимое детализации поста.'''
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        post_author_0 = response.context.get('post').author
        post_text_0 = response.context.get('post').text
        self.assertEqual(post_author_0, self.author)
        self.assertEqual(post_text_0, 'test_text')

    def test_post_create_page_show_correct_context(self):
        '''Проверяется добавления записи с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse('posts:post_create')
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)

    def test_post_edit_page_show_correct_context(self):
        '''Проверяется редактирование записи с правильным контекстом.'''
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk}
            )
        )
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_fields = response.context['form'].fields[value]
                self.assertIsInstance(form_fields, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username='test_author')
        cls.post = Post.objects.bulk_create([Post(author=cls.author,
                                                  text='test_text')] * 13)
        cls.group = Group.objects.create(title='test_title',
                                         slug='test_slug',
                                         description='test_discription')

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    # Выполняется проверка количество постов для страницы index
    def test_index_page_containse_ten_records(self):
        '''Проверяется 10 постов на первой странице index.'''
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_second_page_containse_three_records(self):
        '''Проверяется 3 поста на второй странице index.'''
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 3)

    def test_profile_page_containse_ten_records(self):
        '''Проверяется 10 постов на первой странице profile.'''
        response = self.guest_client.get(reverse(
            'posts:profile',
            args=[self.author.username]))
        self.assertEqual(len(response.context.get('page_obj').object_list), 10)

    def test_profile_page_containse_tree_records(self):
        '''Проверяется 3 поста на первой странице profile.'''
        response = self.guest_client.get(reverse(
            'posts:profile',
            args=[self.author.username]) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 3)

    def test_group_posts_page_containse_ten_records(self):
        '''Проверяется 10 постов на первой странице group_posts.'''
        response = self.guest_client.get(reverse(
            'posts:group_posts',
            args=[self.group.slug]))
        self.assertEqual(len(response.context.get('page_obj').object_list), 0)

    def test_group_posts_page_containse_tree_records(self):
        '''Проверяется 3 поста на первой странице group_posts.'''
        response = self.guest_client.get(reverse(
            'posts:group_posts',
            args=[self.group.slug]) + '?page=2')
        self.assertEqual(len(response.context.get('page_obj').object_list), 0)
