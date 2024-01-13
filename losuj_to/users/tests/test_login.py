from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse_lazy


class TestLoginView(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Client()

    def setUp(self):
        self.email = "pbrqsl@gmail.com"
        self.password = "sdjkajdsk"

    def tearDown(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_should_return_200_when_view_is_get(self):
        expected_sc = 200

        resp = self.client.get(reverse_lazy("login"))
        actual_sc = resp.status_code

        self.assertEqual(actual_sc, expected_sc)

    def test_signup_page_url(self):
        response = self.client.get(reverse_lazy("login"))
        expected_template_used = "users/login.html"
        self.assertTemplateUsed(response, expected_template_used)

    def test_register_page_url(self):
        response = self.client.get(reverse_lazy("register"))
        expected_template_used = "users/register.html"
        self.assertTemplateUsed(response, expected_template_used)

    def test_user_register_using_form_password_redirect(self):
        response = self.client.post(
            reverse_lazy("register"),
            data={
                "email": self.email,
                "password1": self.password,
                "password2": self.password,
            },
        )

        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_user_register_using_form_with_common_password_should_fail(self):
        response = self.client.post(
            reverse_lazy("register"),
            data={
                "email": self.email,
                "password1": "123QWEasd",
                "password2": "123QWEasd",
            },
        )

        users = get_user_model().objects.all()
        common = (
            True if "This password is too common" in str(response.content) else False
        )
        self.assertEqual(users.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(common)

    # def test_user_register_using_manager(self):
    #     get_user_model().objects.create(email=self.email, password=self.password)
    #     users = get_user_model().objects.all()
    #     self.assertEqual(users.count(), 1)
