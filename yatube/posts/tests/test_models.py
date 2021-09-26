from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment, Follow

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Andrey')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст первые 15 символов',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def test_post_models_correct_work_str(self):
        """Проверяем, что у модели Post корректно работает __str__."""
        post = PostModelTest.post
        self.assertEqual(len(str(post)), 15)

    def test_post_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Group',
            'image': 'Картинка'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_post_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст нового поста',
            'pub_date': 'Дата создания поста',
            'author': 'Автор нового поста',
            'group': 'Группа, к которой будет относиться пост'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_correct_work_str(self):
        """Проверяем, что у модели Group корректно работает __str__."""
        group = GroupModelTest.group
        self.assertEqual(group.title, str(group))

    def test_group_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Ссылка группы',
            'description': 'Описание группы',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_group_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        group = GroupModelTest.group
        field_help_texts = {
            'title': 'Название новой группы',
            'slug': 'Ccылка новой группы',
            'description': 'Описание новой группы',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).help_text, expected)


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Comments')
        cls.post = Post.objects.create(
            id=1,
            author=cls.user,
            text='Тестовый текст'
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    def test_comment_models_correct_work_str(self):
        """Проверяем, что у модели Comment корректно работает __str__."""
        comment = CommentModelTest.comment
        self.assertEqual(len(str(comment)), 15)

    def test_comment_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Комментарии поста',
            'author': 'Автор комментария',
            'text': 'Текст',
            'created': 'Дата комментария'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).verbose_name, expected)

    def test_comment_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        comment = CommentModelTest.comment
        field_help_texts = {
            'post': 'Пост с комментариями',
            'author': 'Автор комментария',
            'text': 'Текст нового комментария',
            'created': 'Дата создания комментария'
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    comment._meta.get_field(value).help_text, expected)


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Follower')
        cls.author = User.objects.create_user(username='Author')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_follow_correct_work_str(self):
        """Проверяем, что у модели Follow корректно работает __str__."""
        follow = FollowModelTest.follow
        self.assertEqual(
            f'{self.user} подписался на {self.author}', str(follow)
        )

    def test_follow_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)

    def test_follow_help_text(self):
        """help_text в полях совпадает с ожидаемым."""
        follow = FollowModelTest.follow
        field_help_texts = {
            'user': 'Подписывающийся пользователь',
            'author': 'Пользователь с подписчиками',
        }
        for value, expected in field_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).help_text, expected)
