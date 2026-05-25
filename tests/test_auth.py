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

def test_registro_sucesso(client, db_session):
    response = client.post('/auth/register', data={
        'nome': 'Novo Usuario',
        'email': 'novo@teste.com',
        'senha': 'password123'
    }, follow_redirects=True)
    assert 'Cadastro realizado!'.encode('utf-8') in response.data
    assert User.query.filter_by(email='novo@teste.com').first() is not None

def test_logout(auth_client, setup_data):
    response = auth_client.get('/auth/logout', follow_redirects=True)
    assert 'saiu com sucesso'.encode('utf-8') in response.data

def test_perfil_visualizar(auth_client, setup_data):
    response = auth_client.get('/auth/perfil')
    assert response.status_code == 200
    assert 'cliente@pokeshop.com'.encode('utf-8') in response.data

def test_perfil_atualizar_nome_email(auth_client, setup_data, db_session):
    response = auth_client.post('/auth/perfil', data={
        'nome': 'Cliente Atualizado',
        'email': 'cliente_novo@pokeshop.com'
    }, follow_redirects=True)
    assert 'sucesso'.encode('utf-8') in response.data
    
    user = setup_data['cliente']
    db_session.refresh(user)
    assert user.nome == 'Cliente Atualizado'
    assert user.email == 'cliente_novo@pokeshop.com'

def test_perfil_atualizar_senha_sucesso(auth_client, setup_data, db_session):
    user = setup_data['cliente']
    response = auth_client.post('/auth/perfil', data={
        'nome': user.nome,
        'email': user.email,
        'senha_atual': 'cliente123',
        'nova_senha': 'novasenha123'
    }, follow_redirects=True)
    assert 'sucesso'.encode('utf-8') in response.data
    
    db_session.refresh(user)
    assert user.check_password('novasenha123')

def test_perfil_atualizar_senha_errada(auth_client, setup_data):
    user = setup_data['cliente']
    response = auth_client.post('/auth/perfil', data={
        'nome': user.nome,
        'email': user.email,
        'senha_atual': 'senhaerrada',
        'nova_senha': 'novasenha123'
    }, follow_redirects=True)
    assert 'Senha atual incorreta'.encode('utf-8') in response.data
