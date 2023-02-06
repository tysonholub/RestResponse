import os
import pytest

from tests import test_app
from tests.models import DBModel, test_db

TEST_PATH = os.path.dirname(__file__)


@pytest.fixture
def db():
    with test_app.app_context():
        test_db.create_all()
        test_db.session = test_db._make_scoped_session(dict(expire_on_commit=False))
        yield test_db
        test_db.session.flush()
        test_db.drop_all()


@pytest.fixture
def db_model(db):
    model = DBModel()
    db.session.add(model)
    db.session.commit()
    yield model


@pytest.fixture
def load_template():
    def _load(file, mode):
        with open(os.path.join(TEST_PATH, 'templates', file), mode) as f:
            return f.read()
    return _load


@pytest.fixture
def binary(load_template):
    return load_template('binary', 'rb')


@pytest.fixture
def user_text(load_template):
    return load_template('user.json', 'r').strip()
