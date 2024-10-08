from unittest.mock import Mock

import pytest
from fastapi.testclient import TestClient

from app.auth.dependencies import RoleChecker
from app.db_connection import get_db
from main import app

mock_session = Mock()
mock_user_service = Mock()
mock_book_service = Mock()

role_checker = RoleChecker(['admin'])


def get_mock_session():
    yield mock_session


app.dependency_overrides[get_db] = Mock(side_effect=get_mock_session)
app.dependency_overrides[role_checker] = Mock(side_effect=get_mock_session)


@pytest.fixture
def fake_session():
    return mock_session


@pytest.fixture
def fake_user_service():
    return mock_user_service


@pytest.fixture
def fake_book_service():
    return mock_book_service


@pytest.fixture
def test_client():
    return TestClient(app)
