from django.test import TestCase

from posts.models import Group
from posts.models import Post
from posts.models import User

USERNAME = 'test_author'
TITLE = 'test_group'
SLUG = 'test_slug'
DESCRIPTION = 'test_text'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title=TITLE,
            slug=SLUG,
            description=DESCRIPTION,
        )
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Ж' * 100
        )

    def test_model_post_have_correct_str(self):
        '''Проверяется, что у модели Post корректно работает __str__.'''
        self.assertEqual(self.post.text[:15], str(self.post))

    def test_model_group_have_correct_str(self):
        '''Проверяется, что у модели Group корректно работает __str__.'''
        self.assertEqual(self.group.title, str(self.group))

    def test_verbose_name_model_group(self):
        '''verbose_name в полях модели Group совпадает с ожидаемым.'''
        field_verboses = {
            'title': 'Заголовок',
            'slug': 'Идентификатор',
            'description': 'Описание',
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Group._meta.get_field(field).verbose_name, expected)

    def test_verbose_name_model_post(self):
        '''verbose_name в полях модели Post совпадает с ожидаемым.'''
        field_verboses = {
            'text': 'Текст',
            'pub_date': 'Дата',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    Post._meta.get_field(field).verbose_name, expected)
