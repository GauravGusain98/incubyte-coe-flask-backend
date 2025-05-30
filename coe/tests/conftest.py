import os
import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["ENV"] = "test"

from app import create_app
from coe.models.base import db as _db
from config import Config as TestConfig

engine = create_engine(TestConfig.SQLALCHEMY_DATABASE_URI)

@pytest.fixture(scope="session")
def app():
    app = create_app()
    with app.app_context():
        yield app


@pytest.fixture(scope="session", autouse=True)
def run_migrations():
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")
    command.upgrade(alembic_cfg, "head")
    yield
    command.downgrade(alembic_cfg, "base")
    if "ENV" in os.environ:
        del os.environ["ENV"]


@pytest.fixture(scope="function")
def db(request, app):
    """Provide a new DB session for a test."""
    connection = engine.connect()
    transaction = connection.begin()

    _db.session.bind = connection

    should_rollback = request.node.get_closest_marker("rollback") is not None

    try:
        yield _db.session
    finally:
        _db.session.close()
        if should_rollback:
            transaction.rollback()
        else:
            transaction.commit()
        connection.close()


@pytest.fixture(scope="function")
def client(app, db):
    return app.test_client()
