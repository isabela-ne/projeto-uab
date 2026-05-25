import pytest
from app.models.order import Order

def test_visualizar_historico_pedidos(auth_client, setup_data, db_session):
    # Primeiro cria um pedido para o usuário
    p = setup_data['produtos']['disponivel']
    pedido = Order(
        user_id=setup_data['cliente'].id,
        status='pago',
        payment_method='pix',
        total=150.0,
        endereco_rua='Rua Um',
        endereco_numero='1',
        endereco_bairro='Bairro',
        endereco_cidade='Cidade',
        endereco_estado='SP',
        endereco_cep='00000-000'
    )
    db_session.add(pedido)
    db_session.commit()

    response = auth_client.get('/orders/')
    assert response.status_code == 200
    assert 'pix'.encode('utf-8') in response.data or str(pedido.id).encode('utf-8') in response.data

def test_visualizar_detalhe_pedido(auth_client, setup_data, db_session):
    # Primeiro cria um pedido para o usuário
    pedido = Order(
        user_id=setup_data['cliente'].id,
        status='pago',
        payment_method='pix',
        total=150.0,
        endereco_rua='Rua Um',
        endereco_numero='1',
        endereco_bairro='Bairro',
        endereco_cidade='Cidade',
        endereco_estado='SP',
        endereco_cep='00000-000'
    )
    db_session.add(pedido)
    db_session.commit()

    response = auth_client.get(f'/orders/{pedido.id}')
    assert response.status_code == 200
    assert 'Rua Um'.encode('utf-8') in response.data

def test_acesso_negado_pedido_outro_usuario(auth_client, setup_data, db_session):
    # Cria um pedido para o ADMIN
    pedido = Order(
        user_id=setup_data['admin'].id,
        status='pago',
        payment_method='pix',
        total=150.0,
        endereco_rua='Rua Admin',
        endereco_numero='1',
        endereco_bairro='Bairro',
        endereco_cidade='Cidade',
        endereco_estado='SP',
        endereco_cep='00000-000'
    )
    db_session.add(pedido)
    db_session.commit()

    # Tenta acessar com CLIENTE
    response = auth_client.get(f'/orders/{pedido.id}')
    assert response.status_code == 403

def test_admin_visualizar_pedido_cliente(admin_client, setup_data, db_session):
    # Cria um pedido para o CLIENTE
    pedido = Order(
        user_id=setup_data['cliente'].id,
        status='pago',
        payment_method='pix',
        total=100.0,
        endereco_rua='Rua Cliente',
        endereco_numero='1',
        endereco_bairro='Bairro',
        endereco_cidade='Cidade',
        endereco_estado='SP',
        endereco_cep='00000-000'
    )
    db_session.add(pedido)
    db_session.commit()

    # Tenta acessar com ADMIN
    response = admin_client.get(f'/orders/{pedido.id}')
    assert response.status_code == 200
    assert 'Rua Cliente'.encode('utf-8') in response.data
