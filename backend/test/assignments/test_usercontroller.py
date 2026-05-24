import pytest
import unittest.mock as Mock
from src.controllers.usercontroller import UserController

class TestUserController:

    @pytest.fixture
    def mock_dao(self):
        return Mock.Mock()

    @pytest.fixture
    def controller(self, mock_dao):
        return UserController(dao=mock_dao)

    @pytest.mark.unit
    def test_invalid_email(self, controller):
        with pytest.raises(ValueError):
            controller.get_user_by_email("invalid-email")

    @pytest.mark.unit
    def test_get_user_single(self, controller, mock_dao):
        '''test if value returns the user'''
        testemail = 'JohnDoe@bth.student.se'
        user = {'firstName': 'John', 'lastName': 'Doe', 'email': testemail}
        mock_dao.find.return_value = [user]

        result = controller.get_user_by_email(testemail)

        assert result == user

    @pytest.mark.unit
    def test_get_user_multiple(self, controller, mock_dao, capsys):
        '''This tests multiple users to see what gets returned, and captures the error'''
        testemail = 'JohnDoe@bth.student.se'
        users = [{'firstName': 'John', 'lastName': 'Doe', 'email': testemail}, {'firstName': 'albin', 'lastName': 'Doe', 'email': testemail}]
        mock_dao.find.return_value = users

        result = controller.get_user_by_email(testemail)

        captured = capsys.readouterr() # Capture the output

        assert result["firstName"] == "John"
        assert testemail in captured.out

    @pytest.mark.unit
    def test_get_user_none(self, controller, mock_dao):
        # No users should be returned for this query
        mock_dao.find.return_value = []

        result = controller.get_user_by_email("test@test.com")

        assert result is None

    @pytest.mark.unit
    def test_invalid_DB(self, controller, mock_dao):
        mock_dao.find.side_effect = Exception("DB error")
        
        with pytest.raises(Exception):
            controller.get_user_by_email("test@test.com")

        
