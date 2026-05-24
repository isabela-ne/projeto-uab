from app.models.user import User

def test_login_sucesso(client, setup_data):
    response = client.post('/auth/login', data={
        'email': 'cliente@pokeshop.com',
        'senha': 'cliente123'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert 'Cadastro realizado!'.encode('utf-8') not in response.data # Mensagem de registro, não deve aparecer aqui

def test_login_falha_credenciais_invalidas(client, setup_data):
    response = client.post('/auth/login', data={
        'email': 'cliente@pokeshop.com',
        'senha': 'senha_errada'
    }, follow_redirects=True)
    assert 'E-mail ou senha incorretos.'.encode('utf-8') in response.data

def test_bloqueio_conta_apos_5_tentativas(client, setup_data, db_session):
    email = 'cliente@pokeshop.com'
    for _ in range(5):
        client.post('/auth/login', data={'email': email, 'senha': 'errada'})
    
    # Sexta tentativa
    response = client.post('/auth/login', data={'email': email, 'senha': 'errada'}, follow_redirects=True)
    assert 'Conta bloqueada após 5 tentativas.'.encode('utf-8') in response.data

def test_registro_email_duplicado(client, setup_data):
    response = client.post('/auth/register', data={
        'nome': 'Novo Nome',
        'email': 'cliente@pokeshop.com',
        'senha': 'password123'
    }, follow_redirects=True)
    assert 'Este e-mail já está cadastrado.'.encode('utf-8') in response.data
