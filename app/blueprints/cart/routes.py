from flask import Blueprint, session, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required
from app.models.product import Product
import requests

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/view')
@login_required
def view():
    carrinho = session.get('cart', {})
    total = sum(v['preco'] * v['quantidade'] for v in carrinho.values())
    frete = session.get('frete', None)
    return render_template('cart/carrinho.html', carrinho=carrinho, total=total, frete=frete)

@cart_bp.route('/add/<int:produto_id>', methods=['POST'])
@login_required
def add(produto_id):
    produto = Product.query.get_or_404(produto_id)
    quantidade = int(request.form.get('quantidade', 1))

    if quantidade > produto.estoque:
        flash('Estoque insuficiente!', 'danger')
        return redirect(url_for('catalog.index'))

    carrinho = session.get('cart', {})
    pid = str(produto_id)

    if pid in carrinho:
        carrinho[pid]['quantidade'] += quantidade
    else:
        carrinho[pid] = {
            'nome': produto.nome,
            'preco': produto.preco,
            'quantidade': quantidade
        }

    session['cart'] = carrinho
    session.modified = True
    flash(f'{produto.nome} adicionado ao carrinho!', 'success')
    return redirect(url_for('cart.view'))

@cart_bp.route('/remove/<pid>', methods=['POST'])
@login_required
def remove(pid):
    carrinho = session.get('cart', {})
    carrinho.pop(pid, None)
    session['cart'] = carrinho
    session.modified = True
    flash('Item removido do carrinho.', 'info')
    return redirect(url_for('cart.view'))

@cart_bp.route('/clear', methods=['POST'])
@login_required
def clear():
    session.pop('cart', None)
    session.pop('frete', None)
    flash('Carrinho esvaziado.', 'info')
    return redirect(url_for('cart.view'))

@cart_bp.route('/frete', methods=['POST'])
@login_required
def calcular_frete():
    cep = request.form.get('cep', '').replace('-', '').replace('.', '').strip()

    if len(cep) != 8 or not cep.isdigit():
        flash('CEP inválido. Digite apenas os 8 números.', 'danger')
        return redirect(url_for('cart.view'))

    try:
        # Consulta o CEP para validar se existe
        resp = requests.get(f'https://viacep.com.br/ws/{cep}/json/', timeout=5)
        dados = resp.json()

        if 'erro' in dados:
            flash('CEP não encontrado. Verifique e tente novamente.', 'danger')
            return redirect(url_for('cart.view'))

        # Calcula o frete baseado na região do CEP
        primeiro_digito = int(cep[0])

        # Tabela de frete por região
        if primeiro_digito in [0, 1]:
            # SP
            pac = {'valor': 15.90, 'prazo': 5}
            sedex = {'valor': 28.90, 'prazo': 1}
        elif primeiro_digito in [2, 3]:
            # RJ, ES, MG
            pac = {'valor': 18.90, 'prazo': 7}
            sedex = {'valor': 32.90, 'prazo': 2}
        elif primeiro_digito in [4]:
            # BA, SE
            pac = {'valor': 20.90, 'prazo': 8}
            sedex = {'valor': 35.90, 'prazo': 3}
        elif primeiro_digito in [5]:
            # PE, AL, PB, RN
            pac = {'valor': 22.90, 'prazo': 9}
            sedex = {'valor': 38.90, 'prazo': 3}
        elif primeiro_digito in [6]:
            # CE, PI, MA, PA, AM, AP, RR
            pac = {'valor': 25.90, 'prazo': 10}
            sedex = {'valor': 42.90, 'prazo': 4}
        elif primeiro_digito in [7]:
            # TO, GO, MT, MS, DF
            pac = {'valor': 23.90, 'prazo': 9}
            sedex = {'valor': 39.90, 'prazo': 3}
        else:
            # PR, SC, RS e demais
            pac = {'valor': 19.90, 'prazo': 7}
            sedex = {'valor': 33.90, 'prazo': 2}

        cidade = dados.get('localidade', '')
        estado = dados.get('uf', '')

        session['frete'] = {
            'cep': cep,
            'cidade': cidade,
            'estado': estado,
            'pac': pac,
            'sedex': sedex,
            'escolhido': None
        }
        session.modified = True
        flash(f'Frete calculado para {cidade}/{estado}!', 'success')

    except Exception:
        flash('Erro ao consultar o CEP. Tente novamente.', 'danger')

    return redirect(url_for('cart.view'))

@cart_bp.route('/frete/escolher', methods=['POST'])
@login_required
def escolher_frete():
    tipo = request.form.get('tipo')
    frete = session.get('frete', {})

    if tipo in ['pac', 'sedex'] and frete:
        frete['escolhido'] = tipo
        session['frete'] = frete
        session.modified = True
        flash('Frete selecionado!', 'success')

    return redirect(url_for('cart.view'))