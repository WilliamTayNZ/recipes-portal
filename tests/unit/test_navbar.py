import pytest
from recipe import create_app
from flask import url_for
from utils import get_project_root

TEST_DATA_PATH = get_project_root() / "tests" / "data"

#initialise the flask app to test

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'TEST_DATA_PATH': TEST_DATA_PATH,
        'WTF_CSRF_ENABLED': False,
        'REPOSITORY': 'memory'
    })
    return app

# makes a test client to test HTTP requests

@pytest.fixture
def client(app):
    return app.test_client()

#general testing for the navbar, checks routes for home

def test_navbar(client, app):
    with app.test_request_context():
        url = url_for('home_bp.home')
    resp = client.get(url)
    html = resp.data.decode()

    assert resp.status_code == 200
    assert 'src="/static/assets/logo.png"' in html
    assert 'alt="noodles-logo"' in html
    assert '>HOME<' in html
    assert '>BROWSE<' in html
    assert '>LOGIN<' in html
    assert '>REGISTER<' in html
    # assert '<a href="">PLACEHOLDER</a>' in html

#testing browse routes and implementations

def test_browse_link(client, app):
    with app.test_request_context():
        url = url_for('browse_bp.browse')
    resp = client.get(url)

    assert resp.status_code == 200
    assert 'BROWSE' in resp.data.decode()
