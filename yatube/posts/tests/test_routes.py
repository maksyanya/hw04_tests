from django.test import TestCase
from django.urls import reverse

USERNAME = 'test_author'
SLUG = 'test_slug'
ID = 1


class PostRoutesTests(TestCase):
    def test_urls_correct_use(self):
        '''Проверяется маршруты явных и рассчётных урлов.'''
        self.url_list = [
            [
                '/', 'index', []
            ],
            [
                '/create/', 'post_create', []
            ],
            [
                f'/group/{SLUG}/',
                'group_posts', [SLUG]
            ],
            [
                f'/posts/{ID}/',
                'post_detail', [ID]
            ],
            [
                f'/profile/{USERNAME}/',
                'profile', [USERNAME]
            ],
            [
                f'/posts/{ID}/edit/',
                'post_edit', [ID]
            ]
        ]
        for url, name, parametr in self.url_list:
            self.assertEqual(url, reverse(f'posts:{name}', args=parametr))
