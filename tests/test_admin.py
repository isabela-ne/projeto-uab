def test_acesso_admin_negado_para_cliente(auth_client, setup_data):
    response = auth_client.get('/admin/', follow_redirects=True)
    assert 'restrito'.encode('utf-8') in response.data or 'Acesso'.encode('utf-8') in response.data

def test_acesso_admin_permitido_para_admin(admin_client, setup_data):
    response = admin_client.get('/admin/')
    assert response.status_code == 200
    assert 'Relat'.encode('utf-8') in response.data or 'Produtos'.encode('utf-8') in response.data

def test_admin_criar_produto(admin_client, setup_data, db_session):
    cat_id = setup_data['produtos']['disponivel'].categoria_id
    
    response = admin_client.post('/admin/produtos/novo', data={
        'nome': 'Novo Produto Admin',
        'descricao': 'Desc',
        'preco': 99.9,
        'estoque': 50,
        'categoria_id': cat_id,
        'image_url': 'http://img.jpg'
    }, follow_redirects=True)
    
    assert 'sucesso'.encode('utf-8') in response.data
    from app.models.product import Product
    p = Product.query.filter_by(nome='Novo Produto Admin').first()
    assert p is not None

def test_admin_atualizar_status_pedido(admin_client, setup_data, db_session):
    from app.models.order import Order
    pedido = Order(
        user_id=setup_data['cliente'].id,
        status='aguardando_pagamento',
        payment_method='pix',
        total=150.0,
        endereco_rua='Rua Teste',
        endereco_numero='1',
        endereco_bairro='Centro',
        endereco_cidade='SP',
        endereco_estado='SP',
        endereco_cep='00000-000'
    )
    db_session.add(pedido)
    db_session.commit()
    
    response = admin_client.post(f'/admin/pedidos/{pedido.id}/status', data={
        'status': 'pago'
    }, follow_redirects=True)
    
    assert 'atualizado'.encode('utf-8') in response.data or 'pago'.encode('utf-8') in response.data
    
    db_session.refresh(pedido)
    assert pedido.status == 'pago'

def test_admin_editar_produto(admin_client, setup_data, db_session):
    p = setup_data['produtos']['disponivel']
    response = admin_client.post(f'/admin/produtos/{p.id}/editar', data={
        'nome': 'Pikachu Editado',
        'descricao': 'Nova desc',
        'preco': 160.0,
        'estoque': 5,
        'categoria_id': p.categoria_id,
        'image_url': p.image_url
    }, follow_redirects=True)
    
    assert 'atualizado'.encode('utf-8') in response.data
    db_session.refresh(p)
    assert p.nome == 'Pikachu Editado'

def test_admin_excluir_produto(admin_client, setup_data, db_session):
    p = setup_data['produtos']['disponivel']
    response = admin_client.post(f'/admin/produtos/{p.id}/excluir', follow_redirects=True)
    
    assert 'excluído'.encode('utf-8') in response.data
    from app.models.product import Product
    assert Product.query.get(p.id) is None

def test_admin_visualizar_relatorios(admin_client, setup_data):
    response = admin_client.get('/admin/relatorios')
    assert response.status_code == 200
    assert 'Relat'.encode('utf-8') in response.data
    assert 'Receita'.encode('utf-8') in response.data
