from django.test import TestCase, Client
from http import HTTPStatus


class StaticPagesURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованый клиент
        super().setUpClass()
        self.guest_client = Client()

    def test_about_tech_and_author_url(self):
        """Проверка доступности адресов author и tech."""
        url_names = {
            '/about/author/',
            '/about/tech/',
        }
        for value in url_names:
            response = self.guest_client.get(value)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_tech_author_template(self):
        """Проверка шаблонов для адресов tech и author."""
        templates_url_names = {
            'about/author.html': '/about/author/',
            'about/tech.html': '/about/tech/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(adress=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
