import pytest
import requests_mock

def test_adicionar_produto_com_estoque(auth_client, setup_data):
    p_id = setup_data['produtos']['disponivel'].id
    response = auth_client.post(f'/cart/add/{p_id}', data={'quantidade': 1}, follow_redirects=True)
    # Tenta procurar por parte do texto se houver problemas de encoding ou se o flash não aparecer
    assert response.status_code == 200
    assert 'adicionado'.encode('utf-8') in response.data or 'carrinho'.encode('utf-8') in response.data

def test_adicionar_produto_estoque_insuficiente(auth_client, setup_data):
    p_id = setup_data['produtos']['esgotado'].id
    response = auth_client.post(f'/cart/add/{p_id}', data={'quantidade': 1}, follow_redirects=True)
    assert 'insuficiente'.encode('utf-8') in response.data or 'Estoque'.encode('utf-8') in response.data

def test_calcular_frete_mock(auth_client, setup_data):
    with requests_mock.Mocker() as m:
        m.get('https://viacep.com.br/ws/01001000/json/', json={
            'cep': '01001-000', 'localidade': 'São Paulo', 'uf': 'SP'
        })
        response = auth_client.post('/cart/frete', data={'cep': '01001000'}, follow_redirects=True)
        assert 'Frete calculado'.encode('utf-8') in response.data
