from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from app.extensions import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
        usuario = User.query.filter_by(email=email).first()
        if usuario and usuario.failed_login_attempts >= 5:
            flash('Conta bloqueada após 5 tentativas. Contate o suporte.', 'danger')
            return render_template('auth/login.html')
        if usuario and usuario.check_password(senha):
            usuario.failed_login_attempts = 0
            db.session.commit()
            login_user(usuario)
            return redirect(url_for('catalog.index'))
        else:
            if usuario:
                usuario.failed_login_attempts += 1
                db.session.commit()
            flash('E-mail ou senha incorretos.', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '')
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