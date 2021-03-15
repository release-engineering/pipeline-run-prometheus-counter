# SPDX-License-Identifier: GPL-3.0-or-later
import pytest

import prpc.app
import prpc.db


@pytest.fixture()
def app(request):
    """Create an application for the pytest test."""
    app = prpc.app.create_app()
    # Establish an application context before running the tests. This allows the use of
    # Flask-SQLAlchemy in the test setup.
    ctx = app.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)

    return app


@pytest.fixture()
def client(app):
    """Return Flask application client for the pytest test."""
    return app.test_client()


@pytest.fixture()
def db(app):
    """Create a DB connection for the pytest test."""
    db = prpc.db.DBConnection(app.config["PRPC_DB_PATH"])
    db.create_tables()
    return db
