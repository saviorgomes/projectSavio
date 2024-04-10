import pytest
from app import app, models

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index_not_logged_in(client):
    response = client.get('/')
    assert b'Login' in response.data

def test_index_not_logged_in(client):
    response = client.get('/')
    assert response.status_code == 302
    assert response.headers['Location'] == '/login' 


def test_login(client):
    response = client.post('/login', data=dict(
        username='savio',
        password='savio'
    ), follow_redirects=True)
    assert 'Lista de Usuários' in response.data.decode('utf-8')

def test_register(client):
    response = client.post('/register', data=dict(
        username='new_user',
        password='new_password'
    ), follow_redirects=False)
    assert response.status_code == 302  
    assert response.location == '/login'  # Verifica se o redirecionamento está indo para a página inicial

def test_delete(client):
    with client.session_transaction() as sess:
        sess['username'] = 'savio'
    response = client.get('/delete/teste2')
    assert b'teste' not in response.data
