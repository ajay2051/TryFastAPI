from app.auth.schemas import UserCreate

auth_prefix = f"/api/v1/auth/"

signup_data = {
            "username": "username",
            "email": "email",
            "first_name": "first_name",
            "last_name": "last_name",
            "password": "test123"
        }

def test_user_creation(fake_session, fake_user_service, test_client):
    response = test_client.post(
        url=auth_prefix,
        json= signup_data
    )

    user_data = UserCreate(**signup_data)

    assert response.status_code == 201
    assert fake_user_service.user_exists_called_once()
    assert fake_user_service.user_exists_called_once_with(user_data, fake_session)