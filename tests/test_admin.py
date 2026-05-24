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
