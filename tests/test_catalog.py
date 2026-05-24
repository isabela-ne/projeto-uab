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
