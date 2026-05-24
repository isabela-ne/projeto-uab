from app.extensions import db, login_manager
from flask_login import UserMixin
import bcrypt

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='Cliente')
    failed_login_attempts = db.Column(db.Integer, default=0)
    ativo = db.Column(db.Boolean, default=True)

    def set_password(self, senha):
        salt = bcrypt.gensalt(rounds=12)
        self.password_hash = bcrypt.hashpw(
            senha.encode('utf-8'), salt
        ).decode('utf-8')

    def check_password(self, senha):
        return bcrypt.checkpw(
            senha.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))