from django.test import Client, TestCase
from django.urls import reverse_lazy


class TestLoginView(TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = Client()

    def setUp(self):
        pass

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
