import pytest
from recipe import create_app
from flask import url_for

#initialise the flask app to test

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
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
    assert '<img src="../static/assets/logo.png"' in html
    assert 'alt="noodles-logo"' in html
    assert '>HOME<' in html
    assert '>BROWSE<' in html
    assert '<a href="">PLACEHOLDER</a>' in html

#testing browse routes and implementations

def test_browse_link(client, app):
    with app.test_request_context():
        url = url_for('browse_bp.browse')
    resp = client.get(url)

    assert resp.status_code == 200
    assert 'BROWSE' in resp.data.decode()
