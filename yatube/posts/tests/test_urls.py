from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from ..models import Post, Group, Follow
from http import HTTPStatus
from django.core.cache import cache

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Andrey')
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовый текст'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        #cls.follow = Follow.objects.create(
        #author=cls.user,
        #)

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Noauthor')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_public_url(self):
        """Страница index, group_list, profile, post_detail
        доступны любому пользователю."""
        url_names = {
            '/',
            '/group/test-slug/',
            '/profile/Andrey/',
            '/posts/1/',
        }
        for value in url_names:
            response = self.guest_client.get(value)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location(self):
        """Страница post_create.html доступна
        авторизованному пользователю.
        """
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_redirect_anonymous_on_auth_login(self):
        """Страница /create/ перенаправит анонимного пользователя
        на страницу логина.
        """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/')

    def test_page_not_found_404(self):
        """Запрос к несуществующей странице вернёт ошибку 404."""
        response = self.guest_client.get('/pagenotfound404/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_url_redirect_authorized_no_author_on_post_detail(self):
        """Если пользователь авторизован, но не автор,
        то при попытке редактирования поста
        его перенаправит на страницу с постом.
        """
        response = self.authorized_client.get('/posts/1/edit/', follow=True)
        self.assertRedirects(response, '/posts/1/')

    def test_post_create_edit_for_authorized_author(self):
        """Если пользователь авторизован и автор,
        то ему можно редактировать пост.
        """
        response = self.authorized_author.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_follow_user_to_author(self):
        """Если пользователь авторизован,
        то ему можно подписываться на других пользователей и
        удалять их из подписок.
        """
        url_names = {
            '/profile/Andrey/follow/',
            '/profile/Andrey/unfollow/',
        }
        for value in url_names:
            response = self.authorized_client.get(value)
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_follow_url_redirect_anonymous_on_auth_login(self):
        """Страницы /follow/ и /unfollow/ перенаправят
        анонимного пользователя на страницу логина.
        """
        response = self.guest_client.get(
            '/profile/Andrey/follow/',
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/profile/Andrey/follow/'
        )
        response = self.guest_client.get(
            '/profile/Andrey/unfollow/',
            follow=True
        )
        self.assertRedirects(
            response, '/auth/login/?next=/profile/Andrey/unfollow/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test-slug/': 'posts/group_list.html',
            '/profile/Andrey/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/update_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author.get(address)
                self.assertTemplateUsed(response, template)
