import tempfile
import shutil

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from ..models import Comment, Follow, Post, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_following = User.objects.create_user(username='Andrey')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            id=1,
            author=cls.user_following,
            text='Текст',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='User')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'User'}): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post': '1'}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', args=('1',)): 'posts/create_post.html',
        }
        for reverse_name, template in templates_page_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_list_is_1(self):
        """Удостоверимся, что на страницу index, group_list, profile
        передаётся созданный пост с картинкой.
        """
        page_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Andrey'}),
        }
        for reverse_name in page_names:
            response = self.authorized_client.get(reverse_name)
            self.assertEqual(response.context['page_obj'].count(self.post), 1)
        self.assertEqual(response.context['post'].text, 'Текст')
        self.assertEqual(response.context['post'].image, 'posts/small.gif')

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post': '1'}
        ))
        form_fields = {
            'text': forms.fields.CharField,
        }
        for value, expected in form_fields.items():
            form_field = response.context.get('form').fields.get(value)
        self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['post'].text, 'Текст')
        self.assertEqual(response.context['post'].image, 'posts/small.gif')

    def test_post_create_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_update_post_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_author.get(reverse(
            'posts:post_edit', args=('1',))
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_cache_index_page(self):
        """Тест для проверки кеширования главной страницы."""
        post = Post.objects.create(
            author=self.user,
            text='Кэш-пост',
        )
        content_add = self.authorized_client.get(
            reverse('posts:index')).content
        post.delete()
        content_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertEqual(content_add, content_delete)
        cache.clear()
        content_delete = self.authorized_client.get(
            reverse('posts:index')).content
        self.assertNotEqual(content_add, content_delete)

    def test_user_following_author(self):
        """Проверка того что пользователь может подписаться на автора."""
        Follow.objects.count()
        response = self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': 'Andrey'}),
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'Andrey'}),
        )
        self.assertEqual(Follow.objects.count(), 1)
        self.assertNotEqual(Follow.objects.count(), 2)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.user_following
            ).exists()
        )

    def test_user_unfollow_author(self):
        """Проверка того что пользователь может отписаться на автора."""
        Follow.objects.count()
        self.follow = Follow.objects.create(
            user=self.user,
            author=self.user_following
        )
        response = self.authorized_client.get(reverse(
            'posts:profile_unfollow', kwargs={'username': 'Andrey'}),
            follow=True
        )
        self.assertEqual(Follow.objects.count(), 0)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'Andrey'}),
        )

    def test_user_comment_post(self):
        """Проверка того, что авторизованный пользователь
        может писать комментарии к посту.
        """
        Comment.objects.count()
        comment = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=('1',)),
            data=comment,
            follow=True)

        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post': '1'}),
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertNotEqual(Comment.objects.count(), 2)
        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                text='Тестовый комментарий'
            ).exists()
        )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Unnamed')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        number_of_post = 13
        for posts in range(number_of_post):
            Post.objects.create(
                author=cls.user,
                text='Тестовый текст1 %s' % posts,
                group=cls.group,
                image=uploaded
            )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        cache.clear()

    def test_first_page(self):
        """Проверка: количество постов на первой странице равно 10."""
        page_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Unnamed'}),
        }
        for reverse_name in page_names:
            response = self.guest_client.get(reverse_name)
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page(self):
        """Проверка: количество постов на второй странице равно 3."""
        page_names = {
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'Unnamed'}),
        }
        for reverse_name in page_names:
            response = self.guest_client.get(reverse_name + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
