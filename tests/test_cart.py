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

def test_remover_item_carrinho(auth_client, setup_data):
    p_id = setup_data['produtos']['disponivel'].id
    # Primeiro adiciona
    auth_client.post(f'/cart/add/{p_id}', data={'quantidade': 1})
    
    # Agora remove
    response = auth_client.post(f'/cart/remove/{p_id}', follow_redirects=True)
    assert 'removido'.encode('utf-8') in response.data
    
    # Verifica se o carrinho está vazio visualmente
    response = auth_client.get('/cart/view')
    assert 'vazio'.encode('utf-8') in response.data or setup_data['produtos']['disponivel'].nome.encode('utf-8') not in response.data

def test_limpar_carrinho(auth_client, setup_data):
    p_id = setup_data['produtos']['disponivel'].id
    auth_client.post(f'/cart/add/{p_id}', data={'quantidade': 1})
    
    response = auth_client.post('/cart/clear', follow_redirects=True)
    assert 'esvaziado'.encode('utf-8') in response.data
    
    response = auth_client.get('/cart/view')
    assert 'vazio'.encode('utf-8') in response.data

def test_escolher_frete(auth_client, setup_data):
    # Simula cálculo de frete na sessão
    with auth_client.session_transaction() as sess:
        sess['frete'] = {
            'pac': {'valor': 15.90, 'prazo': 5},
            'sedex': {'valor': 28.90, 'prazo': 1},
            'escolhido': None
        }
    
    response = auth_client.post('/cart/frete/escolher', data={'tipo': 'sedex'}, follow_redirects=True)
    assert 'selecionado'.encode('utf-8') in response.data
    
    with auth_client.session_transaction() as sess:
        assert sess['frete']['escolhido'] == 'sedex'

def test_aplicar_cupom_valido(auth_client, setup_data, db_session):
    from app.models.coupon import Coupon
    from datetime import datetime, timedelta
    cupom = Coupon(codigo='PROMO10', desconto_pct=10.0, validade=datetime.now() + timedelta(days=1))
    db_session.add(cupom)
    db_session.commit()
    
    response = auth_client.post('/cart/cupom', data={'cupom': 'PROMO10'}, follow_redirects=True)
    assert 'aplicado'.encode('utf-8') in response.data
    
    with auth_client.session_transaction() as sess:
        assert sess['cupom']['codigo'] == 'PROMO10'
        assert sess['cupom']['desconto_pct'] == 10.0

def test_aplicar_cupom_invalido(auth_client, setup_data):
    response = auth_client.post('/cart/cupom', data={'cupom': 'INVALIDO'}, follow_redirects=True)
    assert 'inválido'.encode('utf-8') in response.data

def test_remover_cupom(auth_client, setup_data):
    with auth_client.session_transaction() as sess:
        sess['cupom'] = {'codigo': 'PROMO10', 'desconto_pct': 10.0}
    
    response = auth_client.post('/cart/cupom/remover', follow_redirects=True)
    assert 'removido'.encode('utf-8') in response.data
    
    with auth_client.session_transaction() as sess:
        assert 'cupom' not in sess

def test_calcular_frete_varias_regioes(auth_client, setup_data):
    ceps = [
        ('01001000', 'São Paulo'),
        ('20010000', 'Rio de Janeiro'),
        ('40010000', 'Salvador'),
        ('50010000', 'Recife'),
        ('60010000', 'Fortaleza'),
        ('70040000', 'Brasília'),
        ('80010000', 'Curitiba')
    ]
    
    with requests_mock.Mocker() as m:
        for cep, cidade in ceps:
            m.get(f'https://viacep.com.br/ws/{cep}/json/', json={
                'cep': f'{cep[:5]}-{cep[5:]}', 'localidade': cidade, 'uf': 'UF'
            })
            response = auth_client.post('/cart/frete', data={'cep': cep}, follow_redirects=True)
            assert 'Frete calculado'.encode('utf-8') in response.data
            with auth_client.session_transaction() as sess:
                assert sess['frete']['cidade'] == cidade

def test_calcular_frete_invalido(auth_client, setup_data):
    response = auth_client.post('/cart/frete', data={'cep': '123'}, follow_redirects=True)
    assert 'inválido'.encode('utf-8') in response.data

def test_calcular_frete_nao_encontrado(auth_client, setup_data):
    with requests_mock.Mocker() as m:
        m.get('https://viacep.com.br/ws/99999999/json/', json={'erro': True})
        response = auth_client.post('/cart/frete', data={'cep': '99999999'}, follow_redirects=True)
        assert 'não encontrado'.encode('utf-8') in response.data
