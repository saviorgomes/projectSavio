from asyncio.log import logger
import pytest, os
from . import app
from bs4 import BeautifulSoup
import logging
import requests

LOGGER = logging.getLogger(__name__)

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture
def app_url():
    return "http://localhost:5000" 

def test_login_status(client):
    response = client.get('/login')
    assert response.status_code == 200

def test_pagina_logout(client):
    response = client.get('/logout')
    assert response.status_code == 302

def test_pagina_cadastro(client):
    response = client.get('/cadastro')
    assert response.status_code == 200

def test_login_usuario_inexistente(client):
    response = client.post('/cadastro')
    assert response.status_code == 400

def test_login(client):
    response = client.post('/login', data=dict(
        username='teste',
        password='teste'
    ), follow_redirects=True)
    assert b'Logado como teste' in response.data

def test_login_invalid_credentials(client):
    response = client.post('/login', data=dict(
        username='usuario1',
        password='senha_errada'
    ), follow_redirects=True)
    assert b'Credenciais invalidas' in response.data
    assert response.status_code == 200

def test_logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert b'Voce nao esta logado' in response.data
    assert response.status_code == 200

def test_cadastro(client):
    response = client.post('/cadastro', data=dict(
        username='usuarioteste',
        password='novasenha'
    ), follow_redirects=True)
    assert b'Usuario cadastrado com sucesso' in response.data
    assert response.status_code == 200

def test_cadastro_existing_user(client):
    response = client.post('/cadastro', data=dict(
        username='teste',
        password='teste'
    ), follow_redirects=True)
    assert b'Usuario ja existe' in response.data
    assert response.status_code == 200

def test_tela_login_botao_login(app_url):
    response = requests.get(f"{app_url}/login")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    login_button = soup.find('input', {'type': 'submit', 'value': 'Login'})
    assert login_button is not None

def test_tela_cadastro_botao_cadastrar(app_url):
    response = requests.get(f"{app_url}/cadastro")
    assert response.status_code == 200
    soup = BeautifulSoup(response.text, 'html.parser')
    cadastro_button = soup.find('input', {'type': 'submit', 'value': 'Cadastrar'})
    assert cadastro_button is not None