from django.contrib.auth.hashers import make_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import User


class SignUpTestCase(APITestCase):

    def test_empty_request(self):
        url = reverse('signup')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json(),
                             {
                                'username': ['This field is reqiured.'],
                                'password': ['This field is reqiured.'],
                                'password_repeat': ['This field is reqiured.']
                            })

    def test_weak_password(self):
        url = reverse('signup')
        response = self.client.post(url,
                                    {
                                    'username': 'testuser',
                                    'password': 'password1',
                                    'password_repeat': 'password1'
                                    })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_already_exists(self):
        url = reverse('signup')
        User.objects.create(username='testuser', password=make_password('!@#qwe123'))
        response = self.client.post(url,
                                    {
                                        'username': 'testuser',
                                        'password': '$%^qwe123',
                                        'password_repeat': '$%^qwe123'
                                    })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json, {'username':'A user with username already exist.'})

    def test_email_validation(self):
        url = reverse('signup')
        response = self.client.post(url,
                                    {
                                        'username': 'test_user',
                                        'password':'$%^qwe123',
                                        'password_repeat': '$%^qwe123',
                                        'email': 'invalid_email'
                                    })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json, {'email': "Enter a valid email address."})

    def test_passwords_not_matching(self):
        url = reverse('signup')
        response = self.client.post(url,
                                    {
                                        'username': 'test_user',
                                        'password': '$%^qwe123',
                                        'password_repeat': '$%^qwe1231',
                                    })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual(response.json,
                             {"non_field_errors": "Введенные пароли не совпадают! Пожалуйста, попробуйте еще раз."}
                             )

    def test_signup_with_only_required_fields(self):
        url = reverse('signup')
        response = self.client.post(url,
                                    {
                                        'username': 'test_user',
                                        'password': '$%^qwe123',
                                        'password_repeat': '$%^qwe123',
                                    })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.last()
        self.assertDictEqual(response.json,
                             {
                                'id': new_user.id,
                                'username': 'test_user',
                                'first_name': '',
                                'last_name': ''
                             }
                             )
        self.assertNotEqual(new_user.password, '$%^qwe123')
        self.assertTrue(new_user.check_password('$%^qwe123'))

    def test_signup_with_entered_all_fields(self):
        url = reverse('signup')
        response = self.client.post(url,
                                    {
                                        'username': 'test_user_2',
                                        'password': '$%^qwe123',
                                        'password_repeat': '$%^qwe123',
                                        'email': 'test@test.com',
                                        'first_name': 'Hello',
                                        'last_name': 'World'
                                    })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        new_user = User.objects.last()
        self.assertDictEqual(response.json,
                             {
                                 'id': new_user.id,
                                 'username': 'test_user_2',
                                 'email': 'test@test.com',
                                 'first_name': 'Hello',
                                 'last_name': 'World'
                             }
                             )


class LoginTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='test_user',
            password='!@#qwe123',
            email='test@test.com'
        )

    def test_invalid_username(self):
        url = reverse('login')
        response = self.client.post(url,
                                    {
                                        'username': 'something_wrong',
                                        'password': '!@#qwe123'
                                    })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_password(self):
        url = reverse('login')
        response = self.client.post(url,
                                    {
                                        'username': 'test_user',
                                        'password': 'something_wrong'
                                    })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_with_blank_fields(self):
        url = reverse('login')
        response = self.client.post(url,
                                    {
                                        'username': '',
                                        'password': ''
                                    })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertDictEqual(response.json,
                             {
                                'username': "This field may not be blank.",
                                'password': "This field may not be blank."
                             })

    def test_successful_login(self):
        url = reverse('login')
        response = self.client.post(url,
                                    {
                                        'username': 'test_user',
                                        'password': '!@#qwe123'
                                    })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json,
                             {
                                 'id': self.user.id,
                                 'username': 'test_user',
                                 'email': self.user.email,
                                 'first_name': self.user.first_name,
                                 'last_name': self.user.last_name
                             })
        self.assertNotEqual(response.cookies['sessionid'].value, '')


class TestProfile(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='test_user',
            password='!@#qwe123',
            email='test@test.com'
        )

    def test_logout(self):
        url = reverse('profile')
        self.client.login(username='test_user', password='!@#qwe123')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(response.cookies['sessionid'].value, '')

    def test_retrieve_user_data(self):
        url = reverse('profile')
        self.client.login(username='test_user', password='!@#qwe123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(),
                             {
                                 "id": self.user.id,
                                 "username": 'test_user',
                                 "first_name": self.user.first_name,
                                 "last_name": self.user.last_name,
                                 "email": self.user.email
                             })

    def test_patch_user_data(self):
        url = reverse('profile')
        self.client.login(username='test_user', password='!@#qwe123')
        self.assertEqual(self.user.first_name, '')
        response = self.client.patch(url, {'first_name': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(),
                             {
                                 "id": self.user.id,
                                 "username": 'test_user',
                                 "first_name": 'Test',
                                 "last_name": self.user.last_name,
                                 "email": self.user.email
                             })


class TestUpdatePassword(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='test_user',
            password='!@#qwe123',
            email='test@test.com'
        )

    def test_auth_required(self):
        url = reverse('update-password')
        response = self.client.patch(url,
                                     {
                                        'old_password': '!@#qwe123',
                                        'new_password': '!@#qwe123123'
                                     })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_old_password(self):
        url = reverse('update-password')
        response = self.client.patch(url,
                                     {
                                         'old_password': 'something_wrong',
                                         'new_password': '!@#qwe123123'
                                     })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_successful_change(self):
        self.client.login(username='test_user', password='!@#qwe123')
        url = reverse('update-password')
        response = self.client.patch(url,
                                     {
                                         'old_password': '!@#qwe123',
                                         'new_password': '!@#qwe123123'
                                     })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertDictEqual(response.json(), '')
        self.assertNotEqual(self.user.password, '$%^qwe123123')
        self.assertTrue(self.user.check_password('$%^qwe123'))
