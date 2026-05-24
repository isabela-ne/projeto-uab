from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models.user import User
from datetime import datetime, timedelta
from collections import defaultdict
import time

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Rate limiting simples em memória
_tentativas = defaultdict(list)

def checar_rate_limit(ip):
    agora = time.time()
    _tentativas[ip] = [t for t in _tentativas[ip] if agora - t < 300]
    if len(_tentativas[ip]) >= 10:
        return False
    _tentativas[ip].append(agora)
    return True

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ip = request.remote_addr
        if not checar_rate_limit(ip):
            flash('Muitas tentativas. Aguarde 5 minutos.', 'danger')
            return render_template('auth/login.html')
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        usuario = User.query.filter_by(email=email).first()
        if usuario and usuario.failed_login_attempts >= 5:
            flash('Conta bloqueada após 5 tentativas. Contate o suporte.', 'danger')
            return render_template('auth/login.html')
        if usuario and usuario.check_password(senha):
            if not usuario.ativo:
                flash('Conta desativada. Contate o suporte.', 'danger')
                return render_template('auth/login.html')
            usuario.failed_login_attempts = 0
            db.session.commit()
            login_user(usuario)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('catalog.index'))
        else:
            if usuario:
                usuario.failed_login_attempts += 1
                db.session.commit()
            flash('E-mail ou senha incorretos.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome  = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        if len(senha) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'warning')
            return render_template('auth/register.html')
        if User.query.filter_by(email=email).first():
            flash('Este e-mail já está cadastrado.', 'warning')
            return render_template('auth/register.html')
        u = User(nome=nome, email=email, role='Cliente')
        u.set_password(senha)
        db.session.add(u)
        db.session.commit()
        flash('Cadastro realizado! Faça login.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu com sucesso.', 'info')
    return redirect(url_for('auth.login'))
