from django.utils import timezone
from parameterized import parameterized
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from django.urls import reverse
from core.models import User
from goals.models import Board, BoardParticipant, GoalCategory


class BoardCreateTest(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create(
            username='test_user',
            password='!@#qwe123'
        )

    def test_authentication_required(self):
        url = reverse('create-board')
        response = self.client.post(url, {'title': 'board_title'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_board_creation(self):
        self.assertFalse(Board.objects.exists())
        self.client.force_login(self.user)
        url = reverse('create-board')
        response = self.client.post(url, data={'title': 'new_board'})
        self.assertTrue(Board.objects.exists())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        board = Board.objects.last()
        self.assertDictEqual(response.json(), {
                        "id": board.id,
                        "created": timezone.localtime(board.created).isoformat(),
                        "updated": timezone.localtime(board.updated).isoformat(),
                        "title": 'new_board',
                        "is_deleted": False
                        })
        board_participant_list = BoardParticipant.objects.filter(board=board, user=self.user).all()
        self.assertEqual(len(board_participant_list), 1)
        self.assertEqual(board_participant_list[0].role, BoardParticipant.Roles.owner)


class BoardRetrieveTest(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='test_user', password='!@#qwe123')
        self.board = Board.objects.create(title='test_board')
        BoardParticipant.objects.create(board=self.board, user=self.user, role=BoardParticipant.Roles.owner)
        self.url = reverse('retrieve-update-delete-board', kwargs={'pk': self.board.pk})

    @parameterized.expand([
        ('owner', BoardParticipant.Roles.owner),
        ('writer', BoardParticipant.Roles.writer),
        ('reader', BoardParticipant.Roles.reader),
    ])
    def test_one(self, _, role: BoardParticipant | None):
        new_user = User.objects.create_user(username='test_user_2', password='!@#qwe123')
        match role:
            case BoardParticipant.Roles.owner:
                self.client.force_login(self.user)
            case BoardParticipant.Roles.reader | BoardParticipant.Roles.writer:
                self.client.force_login(new_user)
                BoardParticipant.objects.create(board=self.board, user=new_user, role=role)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_is_not_participant(self):
        new_user = User.objects.create_user(username='test_user_2', password='!@#qwe123')
        self.client.force_login(new_user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_deleted_board(self):
        self.board.is_deleted = True
        self.board.save(update_fields=('is_deleted', ))
        self.client.force_login(self.user)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_auth_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class BoardListTest(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='test_user', password='!@#qwe123')
        self.board_1 = Board.objects.create(title='z_test_board')
        self.board_2 = Board.objects.create(title='a_test_board')
        BoardParticipant.objects.create(board=self.board_1, user=self.user, role=BoardParticipant.Roles.owner)
        BoardParticipant.objects.create(board=self.board_2, user=self.user, role=BoardParticipant.Roles.writer)
        self.url = reverse('list-board')

    def test_auth_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_boards_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_expected = [
                                 {
                                     "id": self.board_2.id,
                                     "created": timezone.localtime(self.board_2.created).isoformat(),
                                     "updated": timezone.localtime(self.board_2.updated).isoformat(),
                                     "title": "a_test_board",
                                     "is_deleted": False
                                 },
                                 {
                                     "id": self.board_1.id,
                                     "created": timezone.localtime(self.board_1.created).isoformat(),
                                     "updated": timezone.localtime(self.board_1.updated).isoformat(),
                                     "title": "z_test_board",
                                     "is_deleted": False
                                 }
                            ]
        self.assertListEqual(response.json(), response_expected)

    def test_deleted_board_does_not_display(self):
        deleted_board = Board.objects.create(title='b_test_board', is_deleted=True)
        BoardParticipant.objects.create(board=deleted_board, user=self.user, role=BoardParticipant.Roles.owner)
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_expected = [
            {
                "id": self.board_2.id,
                "created": timezone.localtime(self.board_2.created).isoformat(),
                "updated": timezone.localtime(self.board_2.updated).isoformat(),
                "title": "a_test_board",
                "is_deleted": False
            },
            {
                "id": self.board_1.id,
                "created": timezone.localtime(self.board_1.created).isoformat(),
                "updated": timezone.localtime(self.board_1.updated).isoformat(),
                "title": "z_test_board",
                "is_deleted": False
            }
        ]
        self.assertListEqual(response.json(), response_expected)


class GoalListTest(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(username='test_user', password='!@#qwe123')
        self.board_1 = Board.objects.create(title='z_test_board')
        BoardParticipant.objects.create(board=self.board_1, user=self.user, role=BoardParticipant.Roles.owner)
        self.cat_1 = GoalCategory.objects.create(board=self.board_1, title='test_category_2', user_id=self.user.id)
        self.cat_2 = GoalCategory.objects.create(board=self.board_1, title='test_category_1', user_id=self.user.id)
        self.url = reverse('list-category')

    def test_auth_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_cat_list(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_expected = [
            {
                "id": self.cat_2.id,
                "user": {
                    "id": self.user.id,
                    "username": "test_user",
                    "first_name": "",
                    "last_name": "",
                    "email": ""
                },
                "created": timezone.localtime(self.cat_2.created).isoformat(),
                "updated": timezone.localtime(self.cat_2.updated).isoformat(),
                "title": 'test_category_1',
                "is_deleted": False,
                "board": self.board_1.id
            },
            {
                "id": self.cat_1.id,
                "user": {
                    "id": self.user.id,
                    "username": "test_user",
                    "first_name": "",
                    "last_name": "",
                    "email": ""
                },
                "created": timezone.localtime(self.cat_1.created).isoformat(),
                "updated": timezone.localtime(self.cat_1.updated).isoformat(),
                "title": "test_category_2",
                "is_deleted": False,
                "board": self.board_1.id
            }
        ]
        self.assertListEqual(response.json(), response_expected)
