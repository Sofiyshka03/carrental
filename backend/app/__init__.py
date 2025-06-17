from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import secrets
from datetime import timedelta
import atexit

# Инициализация расширений
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()

def create_app():
    app = Flask(__name__)
    
    # Конфигурация
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc:///?odbc_connect=DRIVER={SQL Server};SERVER=LAPTOP-MIJRB9SS;DATABASE=Automobiles;Trusted_Connection=yes;charset=utf8'
    app.config['SQLALCHEMY_ECHO'] = True
    
    # JWT конфигурация
    app.config['JWT_SECRET_KEY'] = secrets.token_hex(32)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'msg'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Инициализация расширений с приложением
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Регистрация маршрутов
    from .routes import bp
    app.register_blueprint(bp)
    
    # Инициализация планировщика задач
    with app.app_context():
        from .scheduler import start_scheduler
        scheduler = start_scheduler(app)
        # Регистрируем функцию для остановки планировщика при закрытии приложения
        atexit.register(lambda: scheduler.shutdown(wait=False))
    
    @app.route('/')
    def serve_vue():
        return app.send_static_file('index.html')

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({'error': 'Ресурс не найден'}), 404
    
    # Обработчики ошибок JWT
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'msg': 'Токен истек'}), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({'msg': 'Недействительный токен'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({'msg': 'Отсутствует токен доступа'}), 401
    
    return app 