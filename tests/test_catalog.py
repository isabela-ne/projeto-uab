def test_listagem_produtos_disponiveis(client, setup_data):
    response = client.get('/catalog/')
    assert 'Pikachu VMAX'.encode('utf-8') in response.data
    assert 'Escudo Protetor'.encode('utf-8') not in response.data # Esgotado não aparece

def test_busca_produto(client, setup_data):
    # Busca termo existente
    response = client.get('/catalog/?q=Pikachu')
    assert 'Pikachu VMAX'.encode('utf-8') in response.data
    
    # Busca termo inexistente
    response = client.get('/catalog/?q=Inexistente')
    assert 'Pikachu VMAX'.encode('utf-8') not in response.data

def test_filtro_categoria(client, setup_data):
    cat_id = setup_data['produtos']['disponivel'].categoria_id
    response = client.get(f'/catalog/?categoria={cat_id}')
    assert 'Pikachu VMAX'.encode('utf-8') in response.data

def test_detalhe_produto(client, setup_data):
    p = setup_data['produtos']['disponivel']
    response = client.get(f'/catalog/produto/{p.id}')
    assert response.status_code == 200
    assert p.nome.encode('utf-8') in response.data
    assert p.descricao.encode('utf-8') in response.data

def test_avaliar_produto_sucesso(auth_client, setup_data, db_session):
    p = setup_data['produtos']['disponivel']
    response = auth_client.post(f'/catalog/produto/{p.id}/avaliar', data={
        'nota': 5,
        'comentario': 'Ótimo produto!'
    }, follow_redirects=True)
    assert 'Avaliação enviada'.encode('utf-8') in response.data
    
    from app.models.review import Review
    r = Review.query.filter_by(product_id=p.id, usuario_id=setup_data['cliente'].id).first()
    assert r is not None
    assert r.nota == 5

def test_avaliar_produto_nota_invalida(auth_client, setup_data):
    p = setup_data['produtos']['disponivel']
    response = auth_client.post(f'/catalog/produto/{p.id}/avaliar', data={
        'nota': 6,
        'comentario': 'Invalido'
    }, follow_redirects=True)
    assert 'Nota inválida'.encode('utf-8') in response.data

def test_avaliar_produto_duplicado(auth_client, setup_data, db_session):
    p = setup_data['produtos']['disponivel']
    # Primeiro avaliação
    auth_client.post(f'/catalog/produto/{p.id}/avaliar', data={'nota': 5, 'comentario': 'Ok'})
    
    # Segunda tentativa
    response = auth_client.post(f'/catalog/produto/{p.id}/avaliar', data={
        'nota': 4,
        'comentario': 'De novo'
    }, follow_redirects=True)
    assert 'já avaliou'.encode('utf-8') in response.data
