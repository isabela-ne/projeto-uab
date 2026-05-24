def test_checkout_carrinho_vazio(auth_client, setup_data):
    response = auth_client.get('/checkout/', follow_redirects=True)
    assert 'vazio'.encode('utf-8') in response.data or 'carrinho'.encode('utf-8') in response.data

def test_finalizar_pedido_sucesso_e_baixa_estoque(auth_client, setup_data, db_session):
    # Adiciona ao carrinho
    p = setup_data['produtos']['disponivel']
    auth_client.post(f'/cart/add/{p.id}', data={'quantidade': 2})
    
    estoque_inicial = p.estoque
    
    # Finaliza checkout
    response = auth_client.post('/checkout/finalizar', data={
        'rua': 'Rua Teste', 'numero': '123', 'bairro': 'Centro',
        'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01001-000',
        'pagamento': 'pix'
    }, follow_redirects=True)
    
    assert 'sucesso'.encode('utf-8') in response.data or 'Pedido realizado'.encode('utf-8') in response.data
    
    # Verifica estoque
    db_session.refresh(p)
    assert p.estoque == estoque_inicial - 2

def test_checkout_index_com_itens(auth_client, setup_data):
    p = setup_data['produtos']['disponivel']
    auth_client.post(f'/cart/add/{p.id}', data={'quantidade': 1})
    
    response = auth_client.get('/checkout/')
    assert response.status_code == 200
    assert p.nome.encode('utf-8') in response.data

def test_finalizar_pedido_campos_ausentes(auth_client, setup_data):
    p = setup_data['produtos']['disponivel']
    auth_client.post(f'/cart/add/{p.id}', data={'quantidade': 1})
    
    response = auth_client.post('/checkout/finalizar', data={
        'rua': 'Rua Teste',
        # faltam outros campos
    }, follow_redirects=True)
    
    assert 'Preencha todos os campos'.encode('utf-8') in response.data

def test_finalizar_pedido_pagamento_invalido(auth_client, setup_data):
    p = setup_data['produtos']['disponivel']
    auth_client.post(f'/cart/add/{p.id}', data={'quantidade': 1})
    
    response = auth_client.post('/checkout/finalizar', data={
        'rua': 'Rua Teste', 'numero': '123', 'bairro': 'Centro',
        'cidade': 'São Paulo', 'estado': 'SP', 'cep': '01001-000',
        'pagamento': 'dinheiro_na_mao'
    }, follow_redirects=True)
    
    assert 'inválido'.encode('utf-8') in response.data
