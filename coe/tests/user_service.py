from faker import Faker
from coe.services.user_service import create_user, login_user, update_user, remove_user
from coe.schemas.user import CreateUser, UserLogin, UpdateUser
from coe.models.user import User

faker = Faker()


def create_test_user(db, password="testpass"):
    """Helper to create and return a test user along with its credentials."""
    user_data = CreateUser(
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        email=faker.unique.email(),
        password=password
    )
    created_user = create_user(user_data, db)
    return created_user, user_data.email, password


def test_create_user(db):
    _, email, _ = create_test_user(db)
    queried_user = db.query(User).filter_by(email=email).first()
    assert queried_user is not None


def test_login_user_success(db):
    _, email, password = create_test_user(db)
    login_data = UserLogin(email=email, password=password)
    tokens = login_user(login_data, db)
    assert tokens is not None
    assert "access_token" in tokens


def test_login_user_failure(db):
    login_data = UserLogin(email=faker.unique.email(), password="wrongpass")
    result = login_user(login_data, db)
    assert result is None


def test_update_user(db):
    user, _, _ = create_test_user(db)
    update_data = UpdateUser(first_name=faker.first_name())
    updated = update_user(user.id, update_data, db)
    assert updated is True

    refreshed = db.get(User, user.id)
    assert refreshed.first_name == update_data.first_name


def test_remove_user(db):
    user, _, _ = create_test_user(db)
    deleted = remove_user(user.id, db)
    assert deleted is True

    assert db.get(User, user.id) is None
