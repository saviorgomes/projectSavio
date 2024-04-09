from flask import Flask, render_template, request, redirect, session
import requests
import logging
import logging.handlers
import splunklib.client as client
import templates

from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from prometheus_client.exposition import choose_encoder

app = Flask(__name__, static_folder='static', template_folder='templates')

REQUEST_COUNT = Counter('flask_app_request_count', 'Total number of requests received')
REQUEST_LATENCY = Histogram('flask_app_request_latency_seconds', 'Request latency in seconds')

app.secret_key = 'admin123'

# Dados de usuários (simulação de uma base de dados)
usuarios = {
    'teste': 'teste',
    'teste2': 'teste2'
}


@app.route('/')
def index():
    if 'username' in session:
        return 'Logado como ' + session['username'] + '<br><a href="/logout">Logout</a>'
    REQUEST_COUNT.inc()
    return 'Voce nao esta logado<br><a href="/login">Faça login</a>'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in usuarios and usuarios[username] == password:
            session['username'] = username
            return redirect('/')
            REQUEST_COUNT.inc()
        else:
            return 'Credenciais invalidas. <a href="/login">Tente novamente</a>'
    return render_template('login.html')
    REQUEST_COUNT.inc()


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')
    REQUEST_COUNT.inc()


@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username not in usuarios:
            usuarios[username] = password
            return 'Usuario cadastrado com sucesso! <a href="/login">Faça login</a>'
        else:
            return 'Usuario ja existe. <a href="/cadastro">Tente novamente</a>'
    return render_template('cadastro.html')


if __name__ == '__main__':
    app.run(debug=True)

#Prometheus



@app.route('/')
@REQUEST_LATENCY.time()
def hello():
    REQUEST_COUNT.inc()
    return "Hello World!"

@app.route('/metrics')
def metrics():
    encoder, content_type = choose_encoder(None, None, [CONTENT_TYPE_LATEST])
    headers = {'Content-Type': str(content_type)}
    return encoder(generate_latest()), 200, headers



### Splunk
# Configuração do logger para enviar logs para o Splunk
# logger = logging.getLogger('flask_splunk')
# handler = logging.handlers.SysLogHandler(address=('localhost', 514))
# logger.addHandler(handler)
# logger.setLevel(logging.INFO)


# Configuração do logger
logger = logging.getLogger('flask_splunk')
logger.setLevel(logging.INFO)

# Configuração do handler para enviar logs para o Splunk via HEC
hec_handler = logging.StreamHandler()
hec_handler.setLevel(logging.INFO)
hec_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(hec_handler)


# Função para enviar logs para o Splunk via HEC
def send_to_splunk(log_message):
    url = 'http://127.0.0.1:8000/services/collector'
    headers = {
        'Authorization': 'Splunk 75cf6f22-798a-458a-9872-33df931d215a',
        'Content-Type': 'application/json'
    }
    data = {
        'event': log_message
    }
    response = requests.post(url, headers=headers, json=data, verify=False)
    if response.status_code != 200:
        logger.error(f'Failed to send log to Splunk: {response.text}')