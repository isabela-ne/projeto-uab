from flask import Flask, redirect, url_for, render_template
from dotenv import load_dotenv
import os
from app.extensions import db, login_manager, migrate, csrf

def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pokeshop.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.models import user, product, category, order

    from app.blueprints.auth.routes import auth_bp
    from app.blueprints.catalog.routes import catalog_bp
    from app.blueprints.cart.routes import cart_bp
    from app.blueprints.checkout.routes import checkout_bp
    from app.blueprints.orders.routes import orders_bp
    from app.blueprints.support.routes import support_bp
    from app.blueprints.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(checkout_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(support_bp)
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return redirect(url_for('catalog.index'))

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    return app
