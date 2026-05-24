def test_abrir_ticket_sucesso(auth_client, setup_data):
    response = auth_client.post('/support/novo', data={
        'assunto': 'Dúvida sobre entrega',
        'mensagem': 'Quando meu pedido chega?'
    }, follow_redirects=True)
    
    assert 'Chamado aberto'.encode('utf-8') in response.data
    assert 'Dúvida'.encode('utf-8') in response.data

def test_responder_ticket_cliente(auth_client, setup_data, db_session):
    # Cria ticket
    auth_client.post('/support/novo', data={'assunto': 'T1', 'mensagem': 'M1'})
    from app.models.ticket import Ticket
    # Precisamos garantir que pegamos o ticket certo
    t = Ticket.query.filter_by(assunto='T1').first()
    assert t is not None
    
    # Responde
    response = auth_client.post(f'/support/{t.id}', data={
        'mensagem': 'Minha resposta'
    }, follow_redirects=True)
    
    assert 'Resposta enviada'.encode('utf-8') in response.data
    assert 'Minha resposta'.encode('utf-8') in response.data

def test_acesso_ticket_alheio_negado(auth_client, setup_data, db_session, client):
    # Cliente 1 abre ticket (auth_client já é o cliente 1)
    auth_client.post('/support/novo', data={'assunto': 'Privado', 'mensagem': 'X'})
    from app.models.ticket import Ticket
    t = Ticket.query.filter_by(assunto='Privado').first()
    assert t is not None
    t_id = t.id
    
    # Criar e logar como cliente 2 usando um cliente limpo
    from app.models.user import User
    u2 = User(nome="C2", email="c2@pokeshop.com")
    u2.set_password("123")
    db_session.add(u2)
    db_session.commit()
    
    client.post('/auth/login', data={'email': 'c2@pokeshop.com', 'senha': '123'})
    response = client.get(f'/support/{t_id}', follow_redirects=True)
    assert 'Acesso negado'.encode('utf-8') in response.data
