from flask import Blueprint, jsonify, request, send_from_directory, current_app, send_file
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from . import db
from .models import Client, Car, Booking, PhoneNumber, Passport, DriversLicense, AdditionalService, BookingService, Payment, Employee, Fine, BookingFine, Insurance
import os
from werkzeug.utils import secure_filename
from sqlalchemy import text, null

bp = Blueprint('main', __name__)

# Разрешенные расширения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    if Client.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email уже зарегистрирован'}), 400
        
    try:
        # Создаем клиента
        client = Client(
            Фамилия=data['surname'],
            Имя_Отчество=data['name'],
            Пол=data['gender'],
            Дата_рождения=datetime.strptime(data['birthdate'], '%Y-%m-%d'),
            email=data['email'],
            Пароль=data['password']
        )
        db.session.add(client)
        db.session.flush()  # Получаем ID клиента
        
        # Добавляем телефон
        phone = PhoneNumber(
            Номер=data['phone']['number'],
            Тип=data['phone']['type'],
            ID_клиента=client.ID_клиента
        )
        db.session.add(phone)
        
        # Добавляем паспорт
        passport = Passport(
            ID_клиента=client.ID_клиента,
            Серия_Номер=data['passport']['series_number'],
            Дата_выдачи=datetime.strptime(data['passport']['issue_date'], '%Y-%m-%d'),
            Срок_действия=datetime.strptime(data['passport']['expiry_date'], '%Y-%m-%d'),
            Кем_выдан=data['passport']['issued_by'],
            Код_подразделения=data['passport']['department_code']
        )
        db.session.add(passport)
        
        # Добавляем водительское удостоверение
        license = DriversLicense(
            ID_клиента=client.ID_клиента,
            Номер=data['license']['number'],
            Дата_выдачи=datetime.strptime(data['license']['issue_date'], '%Y-%m-%d'),
            Срок_действия=datetime.strptime(data['license']['expiry_date'], '%Y-%m-%d'),
            Место_выдачи=data['license']['issue_place']
        )
        db.session.add(license)
        
        db.session.commit()
        return jsonify({'message': 'Регистрация успешна'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при регистрации: {str(e)}")
        return jsonify({'error': 'Ошибка при регистрации'}), 500

@bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    client = Client.query.filter_by(email=data['email']).first()
    
    if client and client.Пароль == data['password']:
        access_token = create_access_token(identity=str(client.ID_клиента))
        return jsonify({'token': access_token}), 200
        
    return jsonify({'error': 'Неверный email или пароль'}), 401

@bp.route('/api/cars', methods=['GET'])
def get_cars():
    try:
        print("Попытка получения списка автомобилей")
        cars = Car.query.all()
        print(f"Получено автомобилей: {len(cars)}")
        
        result = [{
            'ID_автомобиля': car.ID_автомобиля,
            'Марка': car.Марка,
            'Модель': car.Модель,
            'Год_выпуска': car.Год_выпуска,
            'Категория': car.Категория,
            'Стоимость': float(car.Стоимость) if car.Стоимость else 0,
            'Статус_авто': car.Статус_авто,
            'Дата_техосмотра': car.Дата_техосмотра.strftime('%Y-%m-%d') if car.Дата_техосмотра else None,
            'image': car.image
        } for car in cars]
        
        return jsonify(result)
    except Exception as e:
        print(f"Ошибка при получении списка автомобилей: {str(e)}")
        return jsonify({'error': 'Ошибка при получении списка автомобилей'}), 500

@bp.route('/api/cars/<int:car_id>', methods=['GET'])
def get_car(car_id):
    try:
        car = Car.query.get_or_404(car_id)
        return jsonify({
            'ID_автомобиля': car.ID_автомобиля,
            'Марка': car.Марка,
            'Модель': car.Модель,
            'Год_выпуска': car.Год_выпуска,
            'Категория': car.Категория,
            'Стоимость': float(car.Стоимость) if car.Стоимость else 0,
            'Статус_авто': car.Статус_авто,
            'Дата_техосмотра': car.Дата_техосмотра.strftime('%Y-%m-%d') if car.Дата_техосмотра else None,
            'image': car.image
        })
    except Exception as e:
        print(f"Ошибка при получении автомобиля: {str(e)}")
        return jsonify({'error': 'Ошибка при получении данных автомобиля'}), 500

@bp.route('/api/bookings', methods=['POST'])
@jwt_required()
def create_booking():
    client_id = int(get_jwt_identity())
    data = request.get_json()
    
    try:
        print("Получены данные для бронирования:", data)
        
        # Проверяем обязательные поля
        required_fields = ['car_id', 'start_date', 'end_date', 'payment_method']
        for field in required_fields:
            if field not in data:
                print(f"Отсутствует обязательное поле: {field}")
                return jsonify({'error': f'Отсутствует обязательное поле: {field}'}), 422
        
        # Проверяем формат дат
        try:
            start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
            end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        except ValueError as e:
            print(f"Ошибка в формате даты: {e}")
            return jsonify({'error': 'Неверный формат даты'}), 422
            
        # Проверяем метод оплаты
        if data['payment_method'] not in ['Карта', 'Наличные']:
            print(f"Неверный метод оплаты: {data['payment_method']}")
            return jsonify({'error': 'Неверный метод оплаты'}), 422
            
        # Проверяем автомобиль
        car = Car.query.get_or_404(data['car_id'])
        print(f"Найден автомобиль: {car.Марка} {car.Модель}")  # Отладочная информация
        
        if car.Статус_авто == 'На обслуживании':
            return jsonify({'error': 'Автомобиль на обслуживании'}), 400
            
        # Проверяем даты
        today = datetime.now().date()
        
        print(f"Даты аренды: {start_date} - {end_date}")  # Отладочная информация
        
        # Рассчитываем стоимость аренды
        days = (end_date - start_date).days + 1
        total_cost = float(car.Стоимость) * days
        
        # Добавляем стоимость доп. услуг
        services_cost = 0
        if data.get('services'):
            for service_data in data['services']:
                service = AdditionalService.query.get(service_data['id'])
                if service:
                    services_cost += float(service.Стоимость) * service_data['quantity']
        
        total_cost += services_cost
        print(f"Общая стоимость: {total_cost}")  # Отладочная информация
        
        # Создаем бронирование
        booking = Booking(
            Дата_начала=start_date,
            Дата_окончания=end_date,
            Статус_договора='Активен',
            Стоимость=total_cost,
            ID_клиента=client_id,
            ID_автомобиля=car.ID_автомобиля
        )
        db.session.add(booking)
        db.session.flush()
        
        print(f"Создано бронирование с ID: {booking.ID_договора}")  # Отладочная информация
        
        # Добавляем доп. услуги
        if data.get('services'):
            for service_data in data['services']:
                booking_service = BookingService(
                    ID_договора=booking.ID_договора,
                    ID_услуги=service_data['id'],
                    Количество=service_data['quantity']
                )
                db.session.add(booking_service)
        
        # Создаем запись об оплате
        payment = Payment(
            Дата_оплаты=today,
            Статус_оплаты='В ожидании',
            ID_договора=booking.ID_договора,
            Способ_оплаты=data['payment_method']
        )
        db.session.add(payment)
        
        # Обновляем статус автомобиля если нужно
        if start_date.date() == today:
            car.Статус_авто = 'В аренде'
            print(f"Статус автомобиля обновлен на: В аренде")  # Отладочная информация
        
        db.session.commit()
        return jsonify({'message': 'Бронирование успешно создано'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при создании бронирования: {str(e)}")
        print(f"Тип ошибки: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при создании бронирования'}), 500

@bp.route('/api/client/bookings', methods=['GET'])
@jwt_required()
def get_client_bookings():
    try:
        client_id = int(get_jwt_identity())
        print(f"[DEBUG] Запрос бронирований для клиента ID: {client_id}")
        
        # Получаем бронирования клиента
        bookings = Booking.query.filter_by(ID_клиента=client_id).all()
        print(f"[DEBUG] Найдено {len(bookings)} бронирований для клиента ID: {client_id}")
        
        result = []
        
        for booking in bookings:
            booking_data = {
                'ID_договора': booking.ID_договора,
                'Дата_начала': booking.Дата_начала.strftime('%Y-%m-%d'),
                'Дата_окончания': booking.Дата_окончания.strftime('%Y-%m-%d'),
                'Статус_договора': booking.Статус_договора,
                'Стоимость': float(booking.Стоимость) if booking.Стоимость else 0
            }
            
            # Добавляем информацию об автомобиле, если есть
            if booking.car:
                booking_data['Автомобиль'] = {
                    'ID_автомобиля': booking.car.ID_автомобиля,
                    'Марка': booking.car.Марка,
                    'Модель': booking.car.Модель,
                    'Год_выпуска': booking.car.Год_выпуска,
                    'Категория': booking.car.Категория,
                    'image': booking.car.image
                }
            else:
                booking_data['Автомобиль'] = None
                print(f"[ПРЕДУПРЕЖДЕНИЕ] Для бронирования {booking.ID_договора} не удалось получить данные автомобиля")
            
            result.append(booking_data)
        
        print(f"[DEBUG] Подготовлено {len(result)} результатов для отправки клиенту")
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при получении бронирований: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении списка бронирований'}), 500

# Маршрут для получения штрафов клиента
@bp.route('/api/client/fines', methods=['GET'])
@jwt_required()
def get_client_fines():
    try:
        client_id = int(get_jwt_identity())
        print(f"[DEBUG] Запрос штрафов для клиента ID: {client_id}")
        
        # Проверяем существование клиента
        client = Client.query.get(client_id)
        if not client:
            print(f"[ОШИБКА] Клиент с ID {client_id} не найден в базе данных")
            return jsonify({'error': 'Клиент не найден'}), 404
            
        # Находим все договоры клиента
        bookings = Booking.query.filter_by(ID_клиента=client_id).all()
        if not bookings:
            print(f"[DEBUG] У клиента нет бронирований")
            return jsonify([])
            
        # Получаем все штрафы по договорам клиента
        result = []
        for booking in bookings:
            booking_fines = BookingFine.query.filter_by(ID_договора=booking.ID_договора).all()
            
            for bf in booking_fines:
                fine = Fine.query.get(bf.ID_штрафа)
                if fine:
                    fine_data = {
                        'ID_договора': bf.ID_договора,
                        'ID_штрафа': bf.ID_штрафа,
                        'Название': fine.Название,
                        'Стоимость': float(fine.Стоимость) if fine.Стоимость else 0,
                        'Количество': bf.Количество,
                        'Сумма': float(fine.Стоимость) * float(bf.Количество) if fine.Стоимость else 0
                    }
                    result.append(fine_data)
        
        print(f"[DEBUG] Найдено {len(result)} штрафов для клиента {client_id}")
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при получении штрафов клиента: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении списка штрафов'}), 500

# Маршрут для оплаты штрафа клиентом
@bp.route('/api/client/pay_fine', methods=['POST'])
@jwt_required()
def pay_client_fine():
    try:
        client_id = int(get_jwt_identity())
        print(f"[DEBUG] Запрос на оплату штрафа от клиента ID: {client_id}")
        
        # Получаем данные из запроса
        data = request.get_json()
        if not data or 'contract_id' not in data or 'fine_id' not in data:
            return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
            
        contract_id = data['contract_id']
        fine_id = data['fine_id']
        
        # Проверяем существование договора и принадлежность его клиенту
        booking = Booking.query.get(contract_id)
        if not booking:
            return jsonify({'error': 'Договор не найден'}), 404
            
        if booking.ID_клиента != client_id:
            print(f"[ПРЕДУПРЕЖДЕНИЕ] Попытка оплаты штрафа по чужому договору. Клиент: {client_id}, Владелец договора: {booking.ID_клиента}")
            return jsonify({'error': 'Нет доступа к данному договору'}), 403
            
        # Проверяем существование штрафа по договору
        booking_fine = BookingFine.query.filter_by(ID_договора=contract_id, ID_штрафа=fine_id).first()
        if not booking_fine:
            return jsonify({'error': 'Штраф не найден'}), 404
            
        # Удаляем штраф из базы (считаем оплаченным)
        db.session.delete(booking_fine)
        db.session.commit()
        
        print(f"[DEBUG] Штраф успешно оплачен: Договор {contract_id}, Штраф {fine_id}")
        return jsonify({'message': 'Штраф успешно оплачен'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при оплате штрафа: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при оплате штрафа'}), 500

# Добавим маршрут для получения доп. услуг
@bp.route('/api/services', methods=['GET'])
def get_services():
    services = AdditionalService.query.all()
    return jsonify([{
        'id': service.ID_услуги,
        'name': service.Название,
        'cost': float(service.Стоимость)
    } for service in services])

@bp.route('/api/cars/<int:car_id>/image', methods=['POST'])
@jwt_required()
def upload_car_image(car_id):
    if 'image' not in request.files:
        return jsonify({'error': 'Нет файла'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400
        
    if file and allowed_file(file.filename):
        # Сохраняем файл с тем же именем, что в базе данных
        filename = f"{car_id}.jpg"
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        
        # Обновляем путь к изображению в базе данных
        car = Car.query.get_or_404(car_id)
        car.image = filename
        db.session.commit()
        
        return jsonify({'message': 'Изображение загружено'}), 200
    
    return jsonify({'error': 'Недопустимый тип файла'}), 400

# Маршрут для получения изображений
@bp.route('/static/cars/<path:filename>')
def serve_car_image(filename):
    try:
        return send_file(
            os.path.join(current_app.config['UPLOAD_FOLDER'], filename),
            mimetype='image/jpeg'
        )
    except Exception as e:
        print(f"Ошибка при получении изображения {filename}: {str(e)}")
        return '', 404

# ----------------------- МАРШРУТЫ ДЛЯ СОТРУДНИКОВ -----------------------

@bp.route('/api/employee/login', methods=['POST'])
def employee_login():
    data = request.get_json()
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Отсутствуют данные для входа'}), 400
        
    employee = Employee.query.filter_by(email=data['email']).first()
    
    if employee and employee.Пароль == data['password']:
        # Создаем токен с пометкой, что это сотрудник
        access_token = create_access_token(
            identity=str(employee.ID_сотрудника),
            additional_claims={'role': 'employee'}
        )
        return jsonify({
            'token': access_token,
            'employee': {
                'ID_сотрудника': employee.ID_сотрудника,
                'ФИО': employee.ФИО_с,
                'Должность': employee.Должность
            }
        }), 200
        
    return jsonify({'error': 'Неверный email или пароль'}), 401

# Проверка того, что запрос от сотрудника
def employee_required():
    try:
        from flask_jwt_extended import get_jwt
        claims = get_jwt()
        if claims.get('role') != 'employee':
            return jsonify({'error': 'Доступ запрещен'}), 403
        return None
    except Exception as e:
        print(f"Ошибка при проверке прав сотрудника: {str(e)}")
        return jsonify({'error': 'Ошибка авторизации'}), 401

@bp.route('/api/employee/me', methods=['GET'])
@jwt_required()
def get_employee_info():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    employee_id = get_jwt_identity()
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return jsonify({'error': 'Сотрудник не найден'}), 404
        
    return jsonify({
        'ID_сотрудника': employee.ID_сотрудника,
        'ФИО': employee.ФИО_с,
        'Должность': employee.Должность,
        'email': employee.email,
        'Телефон': employee.Телефон_с
    })

@bp.route('/api/employee/clients', methods=['GET'])
@jwt_required()
def get_employee_clients():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    clients = Client.query.all()
    result = []
    
    for client in clients:
        client_data = {
            'ID_клиента': client.ID_клиента,
            'ФИО': f"{client.Фамилия} {client.Имя_Отчество}",
            'Пол': client.Пол,
            'email': client.email,
            'Телефоны': [{'Номер': phone.Номер, 'Тип': phone.Тип} for phone in client.телефоны]
        }
        result.append(client_data)
    
    return jsonify(result)

@bp.route('/api/employee/contracts', methods=['GET'])
@jwt_required()
def get_employee_contracts():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        query = """
        SELECT д.ID_договора, 
               CONCAT(к.Фамилия, ' ', к.Имя_Отчество) AS Клиент,
               CONCAT(а.Марка, ' ', а.Модель) AS Автомобиль,
               д.Дата_начала, д.Дата_окончания,
               д.Статус_договора, д.Стоимость,
               о.Статус_оплаты
        FROM Договоры д
        JOIN Клиенты к ON д.ID_клиента = к.ID_клиента
        JOIN Автопарк а ON д.ID_автомобиля = а.ID_автомобиля
        LEFT JOIN Оплата о ON д.ID_договора = о.ID_договора
        ORDER BY д.ID_договора DESC
        """
        
        result = db.session.execute(text(query))
        contracts = []
        
        for row in result:
            # Преобразуем строки БД в словарь
            contract = {
                'ID_договора': row[0],
                'Клиент': row[1],
                'Автомобиль': row[2],
                'Дата_начала': row[3].strftime('%Y-%m-%d') if row[3] else None,
                'Дата_окончания': row[4].strftime('%Y-%m-%d') if row[4] else None,
                'Статус_договора': row[5],
                'Стоимость': float(row[6]) if row[6] else 0,
                'Статус_оплаты': row[7] if row[7] else 'В ожидании'
            }
            contracts.append(contract)
        
        return jsonify(contracts)
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при получении списка договоров: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении списка договоров'}), 500

@bp.route('/api/employee/fines', methods=['GET'])
@jwt_required()
def get_employee_fines():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Проверяем наличие штрафов
        fines_count = Fine.query.count()
        print(f"Количество типов штрафов в базе: {fines_count}")
        
        # Если нет штрафов, добавляем стандартные
        if fines_count == 0:
            print("Добавление стандартных типов штрафов...")
            default_fines = [
                {"Название": "Повреждение автомобиля", "Стоимость": 5000.00},
                {"Название": "Просрочка возврата", "Стоимость": 1000.00},
                {"Название": "Загрязнение салона", "Стоимость": 2000.00},
                {"Название": "Утеря документов", "Стоимость": 1500.00},
                {"Название": "Курение в салоне", "Стоимость": 3000.00}
            ]
            
            for fine_data in default_fines:
                fine = Fine(Название=fine_data["Название"], Стоимость=fine_data["Стоимость"])
                db.session.add(fine)
            
            db.session.commit()
            print("Стандартные типы штрафов добавлены")
        
        # Получаем список штрафов (с учетом только что добавленных)
        fines = Fine.query.all()
        print(f"Получено типов штрафов: {len(fines)}")
        
        return jsonify([fine.to_dict() for fine in fines])
    except Exception as e:
        import traceback
        print(f"Ошибка при получении списка штрафов: {str(e)}")
        print(f"Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении списка штрафов'}), 500

@bp.route('/api/employee/contract_fines', methods=['GET'])
@jwt_required()
def get_employee_contract_fines():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        print("Получение штрафов по договорам - начало")
        
        contract_id = request.args.get('contract_id')
        if contract_id:
            # Если указан ID договора, возвращаем штрафы только для этого договора
            print(f"Запрос штрафов для договора: {contract_id}")
            fines = BookingFine.query.filter_by(ID_договора=contract_id).all()
        else:
            # Иначе возвращаем все штрафы по всем договорам
            print("Запрос всех штрафов по всем договорам")
            fines = BookingFine.query.all()
        
        print(f"Найдено штрафов: {len(fines)}")
        
        result = []
        for fine in fines:
            try:
                fine_info = Fine.query.get(fine.ID_штрафа)
                if not fine_info:
                    print(f"ОШИБКА: Не найден штраф с ID={fine.ID_штрафа}")
                    continue
                    
                contract = Booking.query.get(fine.ID_договора)
                if not contract:
                    print(f"ОШИБКА: Не найден договор с ID={fine.ID_договора}")
                    continue
                    
                client = Client.query.get(contract.ID_клиента) if contract.ID_клиента else None
                if not client and contract.ID_клиента:
                    print(f"ОШИБКА: Не найден клиент с ID={contract.ID_клиента}")
                
                fine_data = {
                    'ID_договора': fine.ID_договора,
                    'ID_штрафа': fine.ID_штрафа,
                    'Название_штрафа': fine_info.Название if fine_info else 'Н/Д',
                    'Стоимость_штрафа': float(fine_info.Стоимость) if fine_info and fine_info.Стоимость else 0,
                    'Количество': fine.Количество,
                    'Клиент': f"{client.Фамилия} {client.Имя_Отчество}" if client else 'Н/Д'
                }
                result.append(fine_data)
            except Exception as item_error:
                print(f"Ошибка при обработке штрафа ID={fine.ID_штрафа}: {str(item_error)}")
                continue
        
        print(f"Подготовлено результатов: {len(result)}")
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print(f"Ошибка при получении штрафов по договорам: {str(e)}")
        print(f"Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении штрафов по договорам'}), 500

@bp.route('/api/employee/add_fine', methods=['POST'])
@jwt_required()
def add_fine_to_contract():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    data = request.get_json()
    if not data or 'ID_договора' not in data or 'ID_штрафа' not in data or 'Количество' not in data:
        return jsonify({'error': 'Отсутствуют данные для добавления штрафа'}), 400
    
    try:
        # Проверяем существование договора и штрафа
        contract = Booking.query.get(data['ID_договора'])
        fine = Fine.query.get(data['ID_штрафа'])
        
        if not contract:
            return jsonify({'error': 'Договор не найден'}), 404
        if not fine:
            return jsonify({'error': 'Штраф не найден'}), 404
        
        # Проверяем, есть ли уже такой штраф для этого договора
        existing_fine = BookingFine.query.filter_by(
            ID_договора=data['ID_договора'],
            ID_штрафа=data['ID_штрафа']
        ).first()
        
        if existing_fine:
            # Если уже есть, увеличиваем количество
            existing_fine.Количество += int(data['Количество'])
        else:
            # Иначе создаем новую запись
            booking_fine = BookingFine(
                ID_договора=data['ID_договора'],
                ID_штрафа=data['ID_штрафа'],
                Количество=data['Количество']
            )
            db.session.add(booking_fine)
        
        # Если передан ID сотрудника и он не установлен в договоре, добавляем его
        if 'ID_сотрудника' in data and data['ID_сотрудника'] and not contract.ID_сотрудника:
            contract.ID_сотрудника = data['ID_сотрудника']
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Штраф успешно добавлен'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении штрафа: {str(e)}")
        return jsonify({'error': 'Ошибка при добавлении штрафа'}), 500

@bp.route('/api/employee/add_car', methods=['POST'])
@jwt_required()
def add_car():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    data = request.get_json()
    required_fields = ['Марка', 'Модель', 'Год_выпуска', 'Категория', 'Стоимость', 'Статус_авто']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Отсутствует обязательное поле: {field}'}), 400
    
    try:
        # Создаем новый автомобиль
        car = Car(
            Марка=data['Марка'],
            Модель=data['Модель'],
            Год_выпуска=data['Год_выпуска'],
            Категория=data['Категория'],
            Стоимость=data['Стоимость'],
            Статус_авто=data['Статус_авто'],
            Дата_техосмотра=datetime.strptime(data['Дата_техосмотра'], '%Y-%m-%d') if 'Дата_техосмотра' in data else None,
            image=data.get('image', '')
        )
        
        db.session.add(car)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Автомобиль успешно добавлен',
            'car': {
                'ID_автомобиля': car.ID_автомобиля,
                'Марка': car.Марка,
                'Модель': car.Модель
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении автомобиля: {str(e)}")
        return jsonify({'error': 'Ошибка при добавлении автомобиля'}), 500

@bp.route('/api/employee/reports/fines', methods=['GET'])
@jwt_required()
def get_fines_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    # Получаем параметры фильтрации
    client_id = request.args.get('client_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    print(f"[DEBUG] Фильтры отчета по штрафам: client_id={client_id}, start_date={start_date}, end_date={end_date}")
    
    query = db.session.query(
        BookingFine, Fine, Booking, Client
    ).join(
        Fine, BookingFine.ID_штрафа == Fine.ID_штрафа
    ).join(
        Booking, BookingFine.ID_договора == Booking.ID_договора
    ).join(
        Client, Booking.ID_клиента == Client.ID_клиента
    )
    
    # Применяем фильтры
    if client_id:
        try:
            client_id = int(client_id)
            query = query.filter(Client.ID_клиента == client_id)
        except ValueError:
            print(f"[ERROR] Некорректный ID клиента: {client_id}")
    
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Booking.Дата_начала >= start_date)
        except ValueError:
            print(f"[ERROR] Некорректная дата начала: {start_date}")
    
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Booking.Дата_окончания <= end_date)
        except ValueError:
            print(f"[ERROR] Некорректная дата окончания: {end_date}")
    
    results = query.all()
    report = []
    
    for booking_fine, fine, booking, client in results:
        report.append({
            'ID_договора': booking.ID_договора,
            'Дата_договора_начало': booking.Дата_начала.strftime('%Y-%m-%d') if booking.Дата_начала else None,
            'Дата_договора_конец': booking.Дата_окончания.strftime('%Y-%m-%d') if booking.Дата_окончания else None,
            'Клиент': f"{client.Фамилия} {client.Имя_Отчество}",
            'ID_клиента': client.ID_клиента,
            'Штраф': fine.Название,
            'Стоимость_штрафа': float(fine.Стоимость) if fine.Стоимость else 0,
            'Количество': booking_fine.Количество,
            'Итого': float(fine.Стоимость) * float(booking_fine.Количество) if fine.Стоимость else 0
        })
    
    print(f"[DEBUG] Найдено штрафов: {len(report)}")
    return jsonify(report)

@bp.route('/api/employee/reports/cars', methods=['GET'])
@jwt_required()
def get_cars_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    # Получаем параметры фильтрации
    status = request.args.get('status')
    category = request.args.get('category')
    year_from = request.args.get('year_from')
    year_to = request.args.get('year_to')
    
    print(f"[DEBUG] Фильтры отчета по автомобилям: status={status}, category={category}, year_from={year_from}, year_to={year_to}")
    
    query = Car.query
    
    # Применяем фильтры
    if status:
        query = query.filter(Car.Статус_авто == status)
    if category:
        query = query.filter(Car.Категория == category)
    if year_from:
        try:
            year_from = int(year_from)
            query = query.filter(Car.Год_выпуска >= year_from)
        except ValueError:
            print(f"[ERROR] Некорректный год от: {year_from}")
    if year_to:
        try:
            year_to = int(year_to)
            query = query.filter(Car.Год_выпуска <= year_to)
        except ValueError:
            print(f"[ERROR] Некорректный год до: {year_to}")
    
    cars = query.all()
    report = []
    
    print(f"[DEBUG] Найдено автомобилей: {len(cars)}")
    
    for car in cars:
        # Находим текущий договор для машины, если она в аренде
        current_booking = None
        if car.Статус_авто == 'В аренде':
            current_booking = Booking.query.filter(
                Booking.ID_автомобиля == car.ID_автомобиля,
                Booking.Статус_договора == 'Активен'
            ).first()
        
        car_data = {
            'ID_автомобиля': car.ID_автомобиля,
            'Марка': car.Марка,
            'Модель': car.Модель,
            'Год_выпуска': car.Год_выпуска,
            'Категория': car.Категория,
            'Стоимость': float(car.Стоимость) if car.Стоимость else 0,
            'Статус_авто': car.Статус_авто,
            'Дата_техосмотра': car.Дата_техосмотра.strftime('%Y-%m-%d') if car.Дата_техосмотра else None
        }
        
        if current_booking:
            client = Client.query.get(current_booking.ID_клиента)
            car_data['Текущий_арендатор'] = f"{client.Фамилия} {client.Имя_Отчество}" if client else 'Н/Д'
            car_data['Дата_возврата'] = current_booking.Дата_окончания.strftime('%Y-%m-%d') if current_booking.Дата_окончания else None
        
        report.append(car_data)
    
    return jsonify(report)

@bp.route('/api/employee/reports/clients', methods=['GET'])
@jwt_required()
def get_clients_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    # Получаем параметры фильтрации
    gender = request.args.get('gender')
    bookings_from = request.args.get('bookings_from')
    
    print(f"[DEBUG] Фильтры отчета по клиентам: gender={gender}, bookings_from={bookings_from}")
    
    # Базовый запрос для всех клиентов
    all_clients = Client.query.all()
    report = []
    
    for client in all_clients:
        # Проверяем фильтр по полу
        if gender and client.Пол != gender:
            print(f"[DEBUG] Клиент с ID={client.ID_клиента} пропущен: пол {client.Пол} не соответствует фильтру {gender}")
            continue
            
        # Получаем договоры клиента
        bookings = Booking.query.filter_by(ID_клиента=client.ID_клиента).all()
        
        # Проверяем фильтр по количеству бронирований
        if bookings_from:
            try:
                min_bookings = int(bookings_from)
                if len(bookings) < min_bookings:
                    print(f"[DEBUG] Клиент с ID={client.ID_клиента} пропущен: количество бронирований {len(bookings)} < {min_bookings}")
                    continue  # Пропускаем клиента, если не соответствует фильтру
            except ValueError:
                print(f"[ERROR] Некорректное значение для минимального количества бронирований: {bookings_from}")
        
        # Получаем общую сумму по договорам
        total_cost = sum(float(booking.Стоимость) if booking.Стоимость else 0 for booking in bookings)
        
        # Получаем общую сумму штрафов
        total_fines = 0
        for booking in bookings:
            booking_fines = BookingFine.query.filter_by(ID_договора=booking.ID_договора).all()
            for booking_fine in booking_fines:
                fine = Fine.query.get(booking_fine.ID_штрафа)
                if fine and fine.Стоимость:
                    # Преобразуем Количество в float перед умножением
                    total_fines += float(fine.Стоимость) * float(booking_fine.Количество)
        
        client_data = {
            'ID_клиента': client.ID_клиента,
            'ФИО': f"{client.Фамилия} {client.Имя_Отчество}",
            'email': client.email,
            'Телефоны': [{'Номер': phone.Номер, 'Тип': phone.Тип} for phone in client.телефоны],
            'Количество_договоров': len(bookings),
            'Общая_сумма_договоров': total_cost,
            'Общая_сумма_штрафов': total_fines,
            'Итого': total_cost + total_fines
        }
        
        report.append(client_data)
    
    print(f"[DEBUG] Найдено клиентов: {len(report)}")
    return jsonify(report)

@bp.route('/api/employee/reports/active_clients', methods=['GET'])
@jwt_required()
def get_active_clients_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем параметры фильтрации
        gender = request.args.get('gender')
        
        print(f"[DEBUG] Фильтры отчета по активным клиентам: gender={gender}")
        
        # Получаем текущую дату
        today = datetime.now().date()
        
        # Находим активные договоры (даты окончания >= сегодня и статус "Активен")
        active_bookings = Booking.query.filter(
            Booking.Дата_окончания >= today,
            Booking.Статус_договора == 'Активен'
        ).all()
        
        # Получаем ID клиентов с активными договорами
        active_client_ids = set(booking.ID_клиента for booking in active_bookings)
        
        # Формируем отчет
        report = []
        for client_id in active_client_ids:
            client = Client.query.get(client_id)
            if not client:
                continue
                
            # Проверяем фильтр по полу (в базе пол обозначается 'м', 'ж')
            if gender and client.Пол.lower() != gender.lower():
                continue
                
            # Получаем все активные договоры клиента
            client_active_bookings = [b for b in active_bookings if b.ID_клиента == client_id]
            
            # Получаем информацию о телефонах клиента
            phones = PhoneNumber.query.filter_by(ID_клиента=client_id).all()
            phone_numbers = [{'Номер': phone.Номер, 'Тип': phone.Тип} for phone in phones]
            
            # Формируем список договоров для отчета
            bookings_data = []
            for booking in client_active_bookings:
                car = Car.query.get(booking.ID_автомобиля)
                booking_data = {
                    'ID_договора': booking.ID_договора,
                    'Дата_начала': booking.Дата_начала.strftime('%Y-%m-%d'),
                    'Дата_окончания': booking.Дата_окончания.strftime('%Y-%m-%d'),
                    'Автомобиль': f"{car.Марка} {car.Модель}" if car else "Н/Д",
                    'Стоимость': float(booking.Стоимость) if booking.Стоимость else 0
                }
                bookings_data.append(booking_data)
            
            client_data = {
                'ID_клиента': client.ID_клиента,
                'ФИО': f"{client.Фамилия} {client.Имя_Отчество}",
                'Пол': client.Пол,
                'Дата_рождения': client.Дата_рождения.strftime('%Y-%m-%d') if client.Дата_рождения else None,
                'email': client.email,
                'Телефоны': phone_numbers,
                'Количество_активных_договоров': len(client_active_bookings),
                'Договоры': bookings_data
            }
            report.append(client_data)
        
        print(f"[DEBUG] Найдено активных клиентов: {len(report)}")
        return jsonify(report)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по активным клиентам: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по активным клиентам'}), 500

@bp.route('/api/employee/reports/client_history/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client_history_report(client_id):
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Проверяем существование клиента
        client = Client.query.get_or_404(client_id)
        
        # Получаем все договоры клиента
        bookings = Booking.query.filter_by(ID_клиента=client_id).all()
        
        # Подготовка данных клиента
        client_info = {
            'ID_клиента': client.ID_клиента,
            'ФИО': f"{client.Фамилия} {client.Имя_Отчество}",
            'email': client.email,
            'Телефоны': [{'Номер': phone.Номер, 'Тип': phone.Тип} for phone in client.телефоны]
        }
        
        # Подготовка данных договоров
        bookings_data = []
        for booking in bookings:
            # Получаем информацию об автомобиле
            car = Car.query.get(booking.ID_автомобиля)
            
            # Получаем штрафы по договору
            fines = []
            booking_fines = BookingFine.query.filter_by(ID_договора=booking.ID_договора).all()
            for booking_fine in booking_fines:
                fine = Fine.query.get(booking_fine.ID_штрафа)
                if fine:
                    fine_data = {
                        'ID_штрафа': fine.ID_штрафа,
                        'Название': fine.Название,
                        'Стоимость': float(fine.Стоимость) if fine.Стоимость else 0,
                        'Количество': booking_fine.Количество,
                        'Итого': float(fine.Стоимость) * float(booking_fine.Количество) if fine.Стоимость else 0
                    }
                    fines.append(fine_data)
            
            # Получаем платежи по договору
            payments = []
            booking_payments = Payment.query.filter_by(ID_договора=booking.ID_договора).all()
            for payment in booking_payments:
                payment_data = {
                    'ID_оплаты': payment.ID_оплаты,
                    'Дата_оплаты': payment.Дата_оплаты.strftime('%Y-%m-%d') if payment.Дата_оплаты else None,
                    'Статус_оплаты': payment.Статус_оплаты,
                    'Способ_оплаты': payment.Способ_оплаты
                }
                payments.append(payment_data)
            
            # Получаем дополнительные услуги
            services = []
            booking_services = BookingService.query.filter_by(ID_договора=booking.ID_договора).all()
            for booking_service in booking_services:
                service = AdditionalService.query.get(booking_service.ID_услуги)
                if service:
                    service_data = {
                        'ID_услуги': service.ID_услуги,
                        'Название': service.Название,
                        'Стоимость': float(service.Стоимость) if service.Стоимость else 0,
                        'Количество': booking_service.Количество,
                        'Итого': float(service.Стоимость) * booking_service.Количество if service.Стоимость else 0
                    }
                    services.append(service_data)
            
            # Собираем все данные по договору
            booking_data = {
                'ID_договора': booking.ID_договора,
                'Дата_начала': booking.Дата_начала.strftime('%Y-%m-%d'),
                'Дата_окончания': booking.Дата_окончания.strftime('%Y-%m-%d'),
                'Статус_договора': booking.Статус_договора,
                'Стоимость': float(booking.Стоимость) if booking.Стоимость else 0,
                'Автомобиль': {
                    'ID_автомобиля': car.ID_автомобиля,
                    'Марка': car.Марка,
                    'Модель': car.Модель,
                    'Категория': car.Категория
                } if car else None,
                'Штрафы': fines,
                'Платежи': payments,
                'Услуги': services
            }
            bookings_data.append(booking_data)
        
        # Формируем итоговый отчет
        report = {
            'Клиент': client_info,
            'Договоры': bookings_data
        }
        
        return jsonify(report)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по истории клиента: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по истории клиента'}), 500

@bp.route('/api/employee/add_fine_type', methods=['POST'])
@jwt_required()
def add_fine_type():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    data = request.get_json()
    if not data or 'Название' not in data or 'Стоимость' not in data:
        return jsonify({'error': 'Отсутствуют данные для добавления типа штрафа'}), 400
    
    try:
        # Проверяем существование штрафа с таким названием
        existing_fine = Fine.query.filter_by(Название=data['Название']).first()
        
        if existing_fine:
            return jsonify({'error': 'Штраф с таким названием уже существует'}), 400
        
        # Создаем новый тип штрафа
        fine = Fine(
            Название=data['Название'],
            Стоимость=data['Стоимость']
        )
        
        db.session.add(fine)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Тип штрафа успешно добавлен',
            'fine': fine.to_dict()
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении типа штрафа: {str(e)}")
        return jsonify({'error': 'Ошибка при добавлении типа штрафа'}), 500

# Маршрут для обновления статуса автомобиля сотрудником
@bp.route('/api/employee/update_car_status', methods=['POST'])
@jwt_required()
def update_car_status():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        if not data or 'ID_автомобиля' not in data or 'Статус_авто' not in data:
            return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
            
        car_id = data['ID_автомобиля']
        new_status = data['Статус_авто']
        
        # Проверяем допустимые значения статуса
        valid_statuses = ['Доступен', 'В аренде', 'На обслуживании']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Недопустимый статус. Допустимые значения: {", ".join(valid_statuses)}'}), 400
        
        # Находим автомобиль в базе данных
        car = Car.query.get(car_id)
        if not car:
            return jsonify({'error': 'Автомобиль не найден'}), 404
            
        # Обновляем статус
        car.Статус_авто = new_status
        db.session.commit()
        
        print(f"[DEBUG] Статус автомобиля ID={car_id} обновлен на '{new_status}'")
        return jsonify({'message': 'Статус автомобиля успешно обновлен'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при обновлении статуса автомобиля: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при обновлении статуса автомобиля'}), 500

# Маршрут для получения автомобилей (для сотрудника)
@bp.route('/api/employee/cars', methods=['GET'])
@jwt_required()
def get_employee_cars():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        cars = Car.query.all()
        result = []
        
        for car in cars:
            car_data = {
                'ID_автомобиля': car.ID_автомобиля,
                'Марка': car.Марка,
                'Модель': car.Модель,
                'Год_выпуска': car.Год_выпуска,
                'Категория': car.Категория,
                'Стоимость': float(car.Стоимость) if car.Стоимость else 0,
                'Статус_авто': car.Статус_авто,
                'Дата_техосмотра': car.Дата_техосмотра.strftime('%Y-%m-%d') if car.Дата_техосмотра else None,
                'image': car.image
            }
            result.append(car_data)
            
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при получении списка автомобилей: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении списка автомобилей'}), 500

# Маршрут для обновления стоимости автомобиля
@bp.route('/api/employee/update_car_price', methods=['POST'])
@jwt_required()
def update_car_price():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        if not data or 'ID_автомобиля' not in data or 'Стоимость' not in data:
            return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
            
        car_id = data['ID_автомобиля']
        new_price = data['Стоимость']
        
        # Находим автомобиль в базе данных
        car = Car.query.get(car_id)
        if not car:
            return jsonify({'error': 'Автомобиль не найден'}), 404
            
        # Обновляем стоимость
        car.Стоимость = new_price
        db.session.commit()
        
        print(f"[DEBUG] Стоимость автомобиля ID={car_id} обновлена на '{new_price}'")
        return jsonify({'message': 'Стоимость автомобиля успешно обновлена'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при обновлении стоимости автомобиля: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при обновлении стоимости автомобиля'}), 500

# Маршрут для обновления даты техосмотра автомобиля
@bp.route('/api/employee/update_car_inspection_date', methods=['POST'])
@jwt_required()
def update_car_inspection_date():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        if not data or 'ID_автомобиля' not in data or 'Дата_техосмотра' not in data:
            return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
            
        car_id = data['ID_автомобиля']
        new_date = data['Дата_техосмотра']
        
        # Находим автомобиль в базе данных
        car = Car.query.get(car_id)
        if not car:
            return jsonify({'error': 'Автомобиль не найден'}), 404
            
        # Обновляем дату техосмотра
        try:
            inspection_date = datetime.strptime(new_date, '%Y-%m-%d')
            car.Дата_техосмотра = inspection_date
        except ValueError:
            return jsonify({'error': 'Неверный формат даты'}), 400
            
        db.session.commit()
        
        print(f"[DEBUG] Дата техосмотра автомобиля ID={car_id} обновлена на '{new_date}'")
        return jsonify({'message': 'Дата техосмотра автомобиля успешно обновлена'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при обновлении даты техосмотра автомобиля: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при обновлении даты техосмотра автомобиля'}), 500

@bp.route('/api/bookings/<int:booking_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_booking(booking_id):
    client_id = int(get_jwt_identity())
    
    try:
        # Проверяем существование бронирования
        booking = Booking.query.get_or_404(booking_id)
        
        # Проверяем, что бронирование принадлежит этому клиенту
        if booking.ID_клиента != client_id:
            return jsonify({'error': 'Нет доступа к этому бронированию'}), 403
            
        # Проверяем, что бронирование можно отменить
        start_date = booking.Дата_начала
        now = datetime.now().date()
        
        if start_date <= now or booking.Статус_договора != 'Активен':
            return jsonify({'error': 'Невозможно отменить это бронирование'}), 400
        
        print(f"[INFO] Отмена бронирования ID={booking_id}")
        
        # Обновляем статус автомобиля на "Доступен"
        car_id = booking.ID_автомобиля
        car = Car.query.get(car_id)
        if car and car.Статус_авто == 'В аренде':
            print(f"[INFO] Изменение статуса автомобиля ID={car.ID_автомобиля} с '{car.Статус_авто}' на 'Доступен'")
            car.Статус_авто = 'Доступен'
            db.session.commit()
        
        # Прямое удаление через курсор
        try:
            # Получаем прямое соединение с базой через pyodbc
            raw_conn = db.engine.raw_connection()
            cursor = raw_conn.cursor()
            
            try:
                # Начинаем транзакцию для атомарных операций
                cursor.execute("BEGIN TRANSACTION")
                
                # 1. Удаляем записи из таблицы договоры-услуги
                print("[INFO] Удаление связанных услуг...")
                cursor.execute("DELETE FROM [Договоры_Дополнительные_услуги] WHERE [ID_договора] = ?", booking_id)
                
                # 2. Удаляем записи из таблицы договоры-штрафы
                print("[INFO] Удаление связанных штрафов...")
                cursor.execute("DELETE FROM [Договоры_Штрафы] WHERE [ID_договора] = ?", booking_id)
                
                # 3. Удаляем записи из таблицы оплаты
                print("[INFO] Удаление платежей...")
                cursor.execute("DELETE FROM [Оплата] WHERE [ID_договора] = ?", booking_id)
                
                # 4. Наконец удаляем сам договор
                print("[INFO] Удаление договора...")
                cursor.execute("DELETE FROM [Договоры] WHERE [ID_договора] = ?", booking_id)
                
                # Фиксируем транзакцию
                cursor.execute("COMMIT TRANSACTION")
                print(f"[SUCCESS] Бронирование ID={booking_id} успешно удалено")
                
                raw_conn.commit()
                cursor.close()
                raw_conn.close()
                
                return jsonify({'message': 'Бронирование успешно отменено'}), 200
                
            except Exception as sql_error:
                # Если что-то пошло не так, откатываем транзакцию
                cursor.execute("IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION")
                cursor.close()
                raw_conn.close()
                print(f"[ERROR] Ошибка при выполнении SQL: {str(sql_error)}")
                return jsonify({'error': f'Ошибка при удалении бронирования: {str(sql_error)}'}), 500
                
        except Exception as e:
            print(f"[ERROR] Ошибка при подключении к базе данных: {str(e)}")
            return jsonify({'error': f'Ошибка при подключении к базе данных: {str(e)}'}), 500
        
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Общая ошибка при отмене бронирования: {str(e)}")
        return jsonify({'error': 'Ошибка при отмене бронирования'}), 500

# Маршрут для обновления стоимости типа штрафа
@bp.route('/api/employee/update_fine_price', methods=['POST'])
@jwt_required()
def update_fine_price():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        if not data or 'ID_штрафа' not in data or 'Стоимость' not in data:
            return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
            
        fine_id = data['ID_штрафа']
        new_price = data['Стоимость']
        
        # Находим штраф в базе данных
        fine = Fine.query.get(fine_id)
        if not fine:
            return jsonify({'error': 'Штраф не найден'}), 404
            
        # Обновляем стоимость
        fine.Стоимость = new_price
        db.session.commit()
        
        print(f"[DEBUG] Стоимость штрафа ID={fine_id} обновлена на '{new_price}'")
        return jsonify({'message': 'Стоимость штрафа успешно обновлена'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при обновлении стоимости штрафа: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при обновлении стоимости штрафа'}), 500

@bp.route('/api/employee/reports/overdue_clients', methods=['GET'])
@jwt_required()
def get_overdue_clients_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем параметры фильтрации
        overdue_count = request.args.get('overdue_count')
        overdue_type = request.args.get('type')  # all, payments, fines
        
        print(f"[DEBUG] Фильтры отчета по клиентам с просрочками: overdue_count={overdue_count}, type={overdue_type}")
        
        # Преобразуем overdue_count в число, если он указан
        overdue_count_int = None
        if overdue_count:
            try:
                overdue_count_int = int(float(overdue_count))
                print(f"[DEBUG] Установлен фильтр по количеству просроченных платежей: от {overdue_count_int}")
            except (ValueError, TypeError):
                print(f"[ERROR] Некорректное значение для количества просроченных платежей: {overdue_count}, тип: {type(overdue_count)}")
        
        today = datetime.now().date()
        clients_with_overdue = set()  # Множество ID клиентов с просрочками
        
        # 1. Находим клиентов с просроченными платежами
        overdue_payments_query = db.session.query(Booking, Payment).join(
            Payment, Booking.ID_договора == Payment.ID_договора
        ).filter(
            Payment.Статус_оплаты.in_(['В ожидании', 'Отклонено']),
            Booking.Дата_окончания < today
        )
        
        # Для фильтрации по количеству просроченных платежей
        clients_with_payments = set()
        if overdue_type in [None, 'all', 'payments']:
            for booking, payment in overdue_payments_query.all():
                if booking.ID_клиента:
                    days_overdue = (today - booking.Дата_окончания).days
                    # Просто добавляем клиента в список, фильтрацию сделаем позже
                    clients_with_payments.add(booking.ID_клиента)
            
            # Добавляем клиентов с просроченными платежами в общий список
            clients_with_overdue.update(clients_with_payments)
        
        # 2. Находим клиентов с неоплаченными штрафами
        clients_with_fines = set()
        if overdue_type in [None, 'all', 'fines']:
            print(f"[DEBUG] Поиск клиентов с неоплаченными штрафами...")
            
            # Строим запрос для поиска штрафов по договорам
            fines_query = db.session.query(Booking.ID_клиента, BookingFine).join(
                BookingFine, Booking.ID_договора == BookingFine.ID_договора
            ).distinct()
            
            count_fines = 0
            for booking_id_client, booking_fine in fines_query.all():
                if booking_id_client:
                    clients_with_fines.add(booking_id_client)
                    count_fines += 1
            
            print(f"[DEBUG] Найдено {count_fines} штрафов у {len(clients_with_fines)} клиентов")
            
            # Добавляем клиентов с неоплаченными штрафами в общий список
            clients_with_overdue.update(clients_with_fines)
        
        # Формируем отчет
        report = []
        
        for client_id in clients_with_overdue:
            client = Client.query.get(client_id)
            if not client:
                continue
                
            # Получаем договоры клиента
            bookings = Booking.query.filter_by(ID_клиента=client_id).all()
            
            # Определяем просроченные платежи
            overdue_payments = []
            if overdue_type in [None, 'all', 'payments']:
                for booking in bookings:
                    payments = Payment.query.filter_by(ID_договора=booking.ID_договора).all()
                    for payment in payments:
                        if payment.Статус_оплаты in ['В ожидании', 'Отклонено'] and booking.Дата_окончания < today:
                            days_overdue = (today - booking.Дата_окончания).days
                            payment_data = {
                                'ID_договора': booking.ID_договора,
                                'Дата_начала': booking.Дата_начала.strftime('%Y-%m-%d'),
                                'Дата_окончания': booking.Дата_окончания.strftime('%Y-%m-%d'),
                                'Статус_оплаты': payment.Статус_оплаты,
                                'Просрочено_дней': days_overdue
                            }
                            overdue_payments.append(payment_data)
            
            # Получаем данные о неоплаченных штрафах
            unpaid_fines = []
            if overdue_type in [None, 'all', 'fines']:
                print(f"[DEBUG] Получение штрафов для клиента {client_id}...")
                for booking in bookings:
                    booking_fines = BookingFine.query.filter_by(ID_договора=booking.ID_договора).all()
                    
                    for booking_fine in booking_fines:
                        fine = Fine.query.get(booking_fine.ID_штрафа)
                        if fine:
                            fine_data = {
                                'ID_договора': booking.ID_договора,
                                'ID_штрафа': fine.ID_штрафа,
                                'Название': fine.Название,
                                'Стоимость': float(fine.Стоимость) if fine.Стоимость else 0,
                                'Количество': booking_fine.Количество,
                                'Итого': float(fine.Стоимость) * float(booking_fine.Количество) if fine.Стоимость else 0,
                                'Срок_аренды': f"{booking.Дата_начала.strftime('%Y-%m-%d')} - {booking.Дата_окончания.strftime('%Y-%m-%d')}"
                            }
                            unpaid_fines.append(fine_data)
                
                print(f"[DEBUG] Найдено {len(unpaid_fines)} штрафов для клиента {client_id}")
            
            # Применяем фильтр по количеству просроченных платежей
            payment_count = len(overdue_payments)
            fine_count = len(unpaid_fines)
            total_count = payment_count + fine_count
            
            # Решаем, какое количество проверять в зависимости от типа просрочки
            count_to_check = 0
            if overdue_type == 'payments':
                count_to_check = payment_count
                print(f"[DEBUG] Клиент {client_id}: количество просроченных платежей: {payment_count}")
            elif overdue_type == 'fines':
                count_to_check = fine_count
                print(f"[DEBUG] Клиент {client_id}: количество неоплаченных штрафов: {fine_count}")
            else:  # 'all' или None
                count_to_check = total_count
                print(f"[DEBUG] Клиент {client_id}: общее количество просрочек: {total_count} (платежи: {payment_count}, штрафы: {fine_count})")
            
            if overdue_count_int and count_to_check < overdue_count_int:
                print(f"[DEBUG] Пропускаем клиента {client_id}: количество просрочек {count_to_check} < {overdue_count_int}")
                continue
                
            # Если после фильтрации не осталось ни платежей, ни штрафов, пропускаем клиента
            if (overdue_type == 'payments' and not overdue_payments) or \
               (overdue_type == 'fines' and not unpaid_fines) or \
               (overdue_type == 'all' and not overdue_payments and not unpaid_fines) or \
               (overdue_type is None and not overdue_payments and not unpaid_fines):
                continue
            
            client_data = {
                'ID_клиента': client.ID_клиента,
                'ФИО': f"{client.Фамилия} {client.Имя_Отчество}",
                'email': client.email,
                'Телефоны': [{'Номер': phone.Номер, 'Тип': phone.Тип} for phone in client.телефоны],
                'Просроченные_платежи': overdue_payments,
                'Неоплаченные_штрафы': unpaid_fines
            }
            
            report.append(client_data)
        
        print(f"[DEBUG] Найдено клиентов с просрочками после фильтрации: {len(report)}")
        return jsonify(report)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по клиентам с просрочками: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по клиентам с просрочками'}), 500

@bp.route('/api/employee/reports/cars_in_maintenance', methods=['GET'])
@jwt_required()
def get_cars_in_maintenance_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем параметры фильтрации
        include_maintenance = request.args.get('include_maintenance', 'true').lower() == 'true'
        include_overdue = request.args.get('include_overdue', 'true').lower() == 'true'
        
        print(f"[DEBUG] Фильтры отчета по автомобилям на обслуживании: include_maintenance={include_maintenance}, include_overdue={include_overdue}")
        
        # Получаем текущую дату
        today = datetime.now().date()
        
        # Формируем отчет
        report = {
            'На_обслуживании': [],
            'Просрочен_техосмотр': []
        }
        
        # Заполняем данные по машинам на обслуживании (если фильтр включен)
        if include_maintenance:
            # Находим машины на техобслуживании
            maintenance_cars = Car.query.filter_by(Статус_авто='На обслуживании').all()
            
            for car in maintenance_cars:
                car_data = {
                    'ID_автомобиля': car.ID_автомобиля,
                    'Марка': car.Марка,
                    'Модель': car.Модель,
                    'Год_выпуска': car.Год_выпуска,
                    'Категория': car.Категория,
                    'Стоимость': float(car.Стоимость) if car.Стоимость else 0,
                    'Дата_техосмотра': car.Дата_техосмотра.strftime('%Y-%m-%d') if car.Дата_техосмотра else None
                }
                report['На_обслуживании'].append(car_data)
        
        # Заполняем данные по машинам с просроченным техосмотром (если фильтр включен)
        if include_overdue:
            # Машины с просроченным техосмотром
            overdue_inspection_cars = Car.query.filter(
                Car.Дата_техосмотра.isnot(None),
                Car.Дата_техосмотра < today
            ).all()
            
            for car in overdue_inspection_cars:
                days_overdue = (today - car.Дата_техосмотра).days
                car_data = {
                    'ID_автомобиля': car.ID_автомобиля,
                    'Марка': car.Марка,
                    'Модель': car.Модель,
                    'Год_выпуска': car.Год_выпуска,
                    'Категория': car.Категория,
                    'Стоимость': float(car.Стоимость) if car.Стоимость else 0,
                    'Дата_техосмотра': car.Дата_техосмотра.strftime('%Y-%m-%d'),
                    'Просрочено_дней': days_overdue
                }
                report['Просрочен_техосмотр'].append(car_data)
        
        print(f"[DEBUG] Результаты отчета: На_обслуживании={len(report['На_обслуживании'])}, Просрочен_техосмотр={len(report['Просрочен_техосмотр'])}")
        
        return jsonify(report)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по автомобилям на техобслуживании: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по автомобилям на техобслуживании'}), 500

@bp.route('/api/employee/reports/popular_cars', methods=['GET'])
@jwt_required()
def get_popular_cars_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем параметры для фильтрации
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')
        
        print(f"[DEBUG] Фильтры отчета по популярным моделям: start_date={start_date}, end_date={end_date}, category={category}")
        
        # Формируем базовый запрос для получения всех договоров
        query = Booking.query
        
        # Применяем фильтры по датам, если они указаны
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                query = query.filter(Booking.Дата_начала >= start_date)
            except ValueError:
                pass
                
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                query = query.filter(Booking.Дата_окончания <= end_date)
            except ValueError:
                pass
        
        # Получаем все договоры с учетом фильтров
        bookings = query.all()
        
        # Словарь для подсчета частоты аренды каждого автомобиля
        car_frequency = {}
        
        # Подсчитываем количество аренд для каждого автомобиля
        for booking in bookings:
            car_id = booking.ID_автомобиля
            if car_id in car_frequency:
                car_frequency[car_id] += 1
            else:
                car_frequency[car_id] = 1
        
        # Сортируем автомобили по частоте аренды (от наибольшей к наименьшей)
        sorted_car_ids = sorted(car_frequency.keys(), key=lambda x: car_frequency[x], reverse=True)
        
        # Формируем отчет
        report = []
        
        for car_id in sorted_car_ids:
            car = Car.query.get(car_id)
            if not car:
                continue
                
            # Если указана категория, фильтруем по ней
            if category and car.Категория != category:
                print(f"[DEBUG] Авто ID={car_id} пропущено: категория {car.Категория} не соответствует фильтру {category}")
                continue
                
            # Получаем все договоры для этого автомобиля
            car_bookings = [b for b in bookings if b.ID_автомобиля == car_id]
            
            # Рассчитываем общую выручку от аренды этого автомобиля
            total_revenue = sum(float(b.Стоимость) if b.Стоимость else 0 for b in car_bookings)
            
            # Рассчитываем среднюю продолжительность аренды
            total_days = sum((b.Дата_окончания - b.Дата_начала).days + 1 for b in car_bookings)
            avg_duration = total_days / len(car_bookings) if car_bookings else 0
            
            car_data = {
                'ID_автомобиля': car.ID_автомобиля,
                'Марка': car.Марка,
                'Модель': car.Модель,
                'Год_выпуска': car.Год_выпуска,
                'Категория': car.Категория,
                'Стоимость_в_день': float(car.Стоимость) if car.Стоимость else 0,
                'Количество_аренд': car_frequency[car_id],
                'Общая_выручка': total_revenue,
                'Средняя_продолжительность': round(avg_duration, 1)
            }
            
            report.append(car_data)
        
        print(f"[DEBUG] Найдено автомобилей после применения фильтров: {len(report)}")
        return jsonify(report)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по популярным автомобилям: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по популярным автомобилям'}), 500

@bp.route('/api/employee/reports/active_contracts', methods=['GET'])
@jwt_required()
def get_active_contracts_report():
    """Формирует отчет по активным договорам аренды"""
    # Проверяем права сотрудника
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем информацию о пользователе из токена
        employee_id = get_jwt_identity()
        print(f"[DEBUG] Сотрудник {employee_id} запрашивает отчет по активным договорам")
        
        # Получаем параметры фильтрации
        sort_by = request.args.get('sort_by', 'end_date')
        client_id = request.args.get('client_id')
        
        print(f"[DEBUG] Параметры запроса: sort_by={sort_by}, client_id={client_id}")
        
        # Текущая дата для расчета оставшихся дней
        today = datetime.now().date()
        
        # Базовый запрос для активных договоров
        query = Booking.query.filter(
            Booking.Дата_окончания >= today,
            Booking.Статус_договора == 'Активен'
        )
        
        # Применяем фильтр по клиенту, если указан
        if client_id:
            print(f"[DEBUG] Применяем фильтр по клиенту: {client_id}")
            try:
                # Преобразуем строковый параметр в целое число
                client_id_int = int(client_id)
                query = query.filter(Booking.ID_клиента == client_id_int)
            except ValueError:
                print(f"[ОШИБКА] Неверный формат ID клиента: {client_id}")
                return jsonify({'error': 'Неверный формат ID клиента'}), 400
        
        # Получаем все активные договоры
        active_bookings = query.all()
        print(f"[DEBUG] Найдено активных договоров: {len(active_bookings)}")
        
        # Формируем результат
        result = []
        
        # Для каждого договора получаем дополнительную информацию
        for booking in active_bookings:
            # Информация о клиенте
            client = Client.query.get(booking.ID_клиента)
            if not client:
                print(f"[WARN] Клиент не найден для договора {booking.ID_договора}")
                client_name = "Клиент не найден"
            else:
                client_name = f"{client.Фамилия} {client.Имя_Отчество}"
            
            # Информация об автомобиле
            car = Car.query.get(booking.ID_автомобиля)
            if not car:
                print(f"[WARN] Автомобиль не найден для договора {booking.ID_договора}")
                car_info = "Автомобиль не найден"
            else:
                car_info = f"{car.Марка} {car.Модель}"
            
            # Информация о платежах
            payments = Payment.query.filter_by(ID_договора=booking.ID_договора).all()
            payment_status = "Оплачен"
            for payment in payments:
                if payment.Статус_оплаты != 'Оплачен':
                    payment_status = payment.Статус_оплаты
                    break
            
            # Формируем запись для отчета
            days_left = (booking.Дата_окончания - today).days
            contract_data = {
                'ID_договора': booking.ID_договора,
                'Клиент': client_name,
                'ID_клиента': booking.ID_клиента,
                'Автомобиль': car_info,
                'ID_автомобиля': booking.ID_автомобиля,
                'Дата_начала': booking.Дата_начала.strftime('%Y-%m-%d'),
                'Дата_окончания': booking.Дата_окончания.strftime('%Y-%m-%d'),
                'Осталось_дней': days_left,
                'Стоимость': float(booking.Стоимость) if booking.Стоимость else 0,
                'Статус_оплаты': payment_status
            }
            
            result.append(contract_data)
        
        # Сортировка результата
        if result:
            if sort_by == 'end_date':
                result.sort(key=lambda x: x['Осталось_дней'])
                print("[DEBUG] Результат отсортирован по дате окончания")
            elif sort_by == 'start_date':
                result.sort(key=lambda x: x['Дата_начала'])
                print("[DEBUG] Результат отсортирован по дате начала")
            elif sort_by == 'client':
                result.sort(key=lambda x: x['Клиент'])
                print("[DEBUG] Результат отсортирован по имени клиента")
            elif sort_by == 'car':
                result.sort(key=lambda x: x['Автомобиль'])
                print("[DEBUG] Результат отсортирован по автомобилю")
            else:
                result.sort(key=lambda x: x['Осталось_дней'])
                print(f"[DEBUG] Результат отсортирован по умолчанию (осталось дней), т.к. параметр sort_by={sort_by} не распознан")
        
        print(f"[DEBUG] Итоговое количество записей в отчете: {len(result)}")
        if result:
            print(f"[DEBUG] Пример первой записи: {result[0]}")
        
        return jsonify(result)
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Ошибка при формировании отчета по активным договорам: {str(e)}")
        print(f"[ERROR] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': f'Ошибка при формировании отчета: {str(e)}'}), 500

@bp.route('/api/employee/reports/completed_contracts', methods=['GET'])
@jwt_required()
def get_completed_contracts_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем параметры фильтрации
        period = request.args.get('period', 'month')  # по умолчанию за месяц
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        today = datetime.now().date()
        
        # Определяем даты начала и конца периода, если не указаны явно
        if not start_date or not end_date:
            if period == 'month':
                # За последний месяц
                start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
                end_date = today
            elif period == 'quarter':
                # За последний квартал (3 месяца)
                month = today.month
                quarter_start_month = ((month - 1) // 3) * 3 + 1
                start_date = today.replace(month=quarter_start_month, day=1)
                end_date = today
            elif period == 'year':
                # За последний год
                start_date = today.replace(year=today.year - 1)
                end_date = today
            else:
                # За все время
                start_date = None
                end_date = today
        else:
            # Если даты указаны явно, преобразуем их
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Неверный формат даты'}), 400
        
        # Находим завершенные договоры за указанный период
        query = Booking.query.filter(Booking.Статус_договора == 'Завершен')
        
        if start_date:
            query = query.filter(Booking.Дата_окончания >= start_date)
        if end_date:
            query = query.filter(Booking.Дата_окончания <= end_date)
        
        completed_bookings = query.all()
        
        # Формируем отчет
        report = {
            'Период': {
                'Начало': start_date.strftime('%Y-%m-%d') if start_date else 'Все время',
                'Конец': end_date.strftime('%Y-%m-%d')
            },
            'Количество_договоров': len(completed_bookings),
            'Общая_выручка': sum(float(b.Стоимость) if b.Стоимость else 0 for b in completed_bookings),
            'Договоры': []
        }
        
        for booking in completed_bookings:
            # Получаем данные о клиенте
            client = Client.query.get(booking.ID_клиента)
            client_name = f"{client.Фамилия} {client.Имя_Отчество}" if client else "Н/Д"
            
            # Получаем данные об автомобиле
            car = Car.query.get(booking.ID_автомобиля)
            car_info = f"{car.Марка} {car.Модель}" if car else "Н/Д"
            
            # Данные о договоре
            booking_data = {
                'ID_договора': booking.ID_договора,
                'Клиент': client_name,
                'ID_клиента': booking.ID_клиента,
                'Автомобиль': car_info,
                'ID_автомобиля': booking.ID_автомобиля,
                'Дата_начала': booking.Дата_начала.strftime('%Y-%m-%d'),
                'Дата_окончания': booking.Дата_окончания.strftime('%Y-%m-%d'),
                'Длительность_дней': (booking.Дата_окончания - booking.Дата_начала).days + 1,
                'Стоимость': float(booking.Стоимость) if booking.Стоимость else 0
            }
            
            report['Договоры'].append(booking_data)
        
        # Сортируем договоры по дате окончания (сначала недавние)
        report['Договоры'].sort(key=lambda x: x['Дата_окончания'], reverse=True)
        
        return jsonify(report)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по завершенным договорам: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по завершенным договорам'}), 500

@bp.route('/api/employee/reports/overdue_payments', methods=['GET'])
@jwt_required()
def get_overdue_payments_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем параметры фильтрации
        min_days = request.args.get('min_days')
        sort_by = request.args.get('sort_by', 'days')  # days, amount, client
        
        print(f"[DEBUG] Фильтры отчета по просроченным платежам: min_days={min_days}, sort_by={sort_by}")
        
        # Преобразуем min_days в целое число, если указан
        min_days_int = None
        if min_days:
            try:
                min_days_int = int(min_days)
                print(f"[DEBUG] Установлен фильтр по минимальной просрочке: {min_days_int} дней")
            except ValueError:
                print(f"[ERROR] Некорректное значение для минимального количества дней просрочки: {min_days}")
                return jsonify({'error': 'Некорректное значение для параметра min_days'}), 400
        
        today = datetime.now().date()
        
        # Находим договоры с просроченной оплатой
        # (дата окончания < сегодня, но статус платежа не "Оплачен")
        overdue_bookings = db.session.query(Booking, Payment).join(
            Payment, Booking.ID_договора == Payment.ID_договора
        ).filter(
            Booking.Дата_окончания < today,
            Payment.Статус_оплаты.in_(['В ожидании', 'Отклонено'])
        ).all()
        
        print(f"[DEBUG] Найдено просроченных платежей до фильтрации: {len(overdue_bookings)}")
        
        # Формируем отчет
        report = []
        
        for booking, payment in overdue_bookings:
            # Рассчитываем просрочку
            days_overdue = (today - booking.Дата_окончания).days
            
            # Фильтруем по минимальному количеству дней просрочки
            if min_days_int and days_overdue < min_days_int:
                print(f"[DEBUG] Платеж с ID={payment.ID_оплаты} пропущен: просрочка {days_overdue} дней < {min_days_int}")
                continue
            
            # Получаем данные о клиенте
            client = Client.query.get(booking.ID_клиента)
            client_name = f"{client.Фамилия} {client.Имя_Отчество}" if client else "Н/Д"
            
            # Получаем телефоны клиента
            phones = []
            if client:
                phone_numbers = PhoneNumber.query.filter_by(ID_клиента=client.ID_клиента).all()
                phones = [phone.Номер for phone in phone_numbers]
            
            # Получаем данные об автомобиле
            car = Car.query.get(booking.ID_автомобиля)
            car_info = f"{car.Марка} {car.Модель}" if car else "Н/Д"
            
            # Данные о просроченном платеже
            payment_data = {
                'ID_договора': booking.ID_договора,
                'ID_оплаты': payment.ID_оплаты,
                'Клиент': client_name,
                'ID_клиента': booking.ID_клиента,
                'email': client.email if client else "Н/Д",
                'Телефоны': phones,
                'Автомобиль': car_info,
                'ID_автомобиля': booking.ID_автомобиля,
                'Дата_начала': booking.Дата_начала.strftime('%Y-%m-%d'),
                'Дата_окончания': booking.Дата_окончания.strftime('%Y-%m-%d'),
                'Просрочено_дней': days_overdue,
                'Стоимость': float(booking.Стоимость) if booking.Стоимость else 0,
                'Статус_оплаты': payment.Статус_оплаты,
                'Способ_оплаты': payment.Способ_оплаты
            }
            
            report.append(payment_data)
        
        print(f"[DEBUG] Найдено просроченных платежей после фильтрации: {len(report)}")
        
        # Сортируем отчет в зависимости от выбранного поля
        if sort_by == 'days':
            # Сортируем по длительности просрочки (сначала самые длительные)
            report.sort(key=lambda x: x['Просрочено_дней'], reverse=True)
        elif sort_by == 'amount':
            # Сортируем по сумме (сначала самые большие)
            report.sort(key=lambda x: x['Стоимость'], reverse=True)
        elif sort_by == 'client':
            # Сортируем по имени клиента (по алфавиту)
            report.sort(key=lambda x: x['Клиент'])
        else:
            # По умолчанию сортируем по длительности просрочки
            report.sort(key=lambda x: x['Просрочено_дней'], reverse=True)
        
        return jsonify(report)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по просроченным платежам: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по просроченным платежам'}), 500

@bp.route('/api/employee/reports/revenue', methods=['GET'])
@jwt_required()
def get_revenue_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем параметры фильтрации
        period = request.args.get('period', 'month')  # по умолчанию за месяц
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        today = datetime.now().date()
        
        # Определяем даты начала и конца периода, если не указаны явно
        if not start_date or not end_date:
            if period == 'month':
                # За последний месяц
                start_date = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
                end_date = today
            elif period == 'quarter':
                # За последний квартал (3 месяца)
                month = today.month
                quarter_start_month = ((month - 1) // 3) * 3 + 1
                start_date = today.replace(month=quarter_start_month, day=1)
                end_date = today
            elif period == 'year':
                # За последний год
                start_date = today.replace(year=today.year - 1)
                end_date = today
            else:
                # За все время
                start_date = None
                end_date = today
        else:
            # Если даты указаны явно, преобразуем их
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({'error': 'Неверный формат даты'}), 400
        
        # Базовый запрос для всех договоров за период
        query = Booking.query
        
        if start_date:
            query = query.filter(Booking.Дата_начала >= start_date)
        if end_date:
            query = query.filter(Booking.Дата_окончания <= end_date)
        
        bookings = query.all()
        
        # Рассчитываем выручку
        total_revenue = sum(float(booking.Стоимость) if booking.Стоимость else 0 for booking in bookings)
        
        # Рассчитываем выручку по категориям автомобилей
        revenue_by_category = {}
        for booking in bookings:
            car = Car.query.get(booking.ID_автомобиля)
            if not car:
                continue
                
            category = car.Категория or 'Не указана'
            booking_revenue = float(booking.Стоимость) if booking.Стоимость else 0
            
            if category in revenue_by_category:
                revenue_by_category[category] += booking_revenue
            else:
                revenue_by_category[category] = booking_revenue
        
        # Рассчитываем выручку по методам оплаты
        revenue_by_payment_method = {}
        for booking in bookings:
            payments = Payment.query.filter_by(ID_договора=booking.ID_договора).all()
            booking_revenue = float(booking.Стоимость) if booking.Стоимость else 0
            
            for payment in payments:
                method = payment.Способ_оплаты or 'Не указан'
                
                if method in revenue_by_payment_method:
                    revenue_by_payment_method[method] += booking_revenue
                else:
                    revenue_by_payment_method[method] = booking_revenue
        
        # Формируем отчет
        report = {
            'Период': {
                'Начало': start_date.strftime('%Y-%m-%d') if start_date else 'Все время',
                'Конец': end_date.strftime('%Y-%m-%d')
            },
            'Общая_выручка': total_revenue,
            'Количество_договоров': len(bookings),
            'Выручка_по_категориям': [
                {'Категория': category, 'Сумма': amount}
                for category, amount in revenue_by_category.items()
            ],
            'Выручка_по_способам_оплаты': [
                {'Способ_оплаты': method, 'Сумма': amount}
                for method, amount in revenue_by_payment_method.items()
            ]
        }
        
        return jsonify(report)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по выручке: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по выручке'}), 500

@bp.route('/api/employee/reports/popular_services', methods=['GET'])
@jwt_required()
def get_popular_services_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Получаем параметры фильтрации
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        today = datetime.now().date()
        
        # Определяем даты, если не указаны явно
        if start_date:
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                print(f"[ОШИБКА] Неверный формат начальной даты: {start_date}")
                return jsonify({
                    'error': 'Неверный формат начальной даты', 
                    'Период': {
                        'Начало': 'Нет данных',
                        'Конец': 'Нет данных'
                    },
                    'Общее_количество_договоров': 0,
                    'Общая_выручка_от_услуг': 0,
                    'Услуги': []
                }), 400
        
        if end_date:
            try:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                print(f"[ОШИБКА] Неверный формат конечной даты: {end_date}")
                return jsonify({
                    'error': 'Неверный формат конечной даты', 
                    'Период': {
                        'Начало': 'Нет данных',
                        'Конец': 'Нет данных'
                    },
                    'Общее_количество_договоров': 0,
                    'Общая_выручка_от_услуг': 0,
                    'Услуги': []
                }), 400
        
        # Базовый запрос для получения всех договоров
        booking_query = Booking.query
        
        # Применяем фильтры, если они указаны
        if start_date:
            booking_query = booking_query.filter(Booking.Дата_начала >= start_date)
        if end_date:
            booking_query = booking_query.filter(Booking.Дата_окончания <= end_date)
        
        # Получаем договоры
        bookings = booking_query.all()
        booking_ids = [booking.ID_договора for booking in bookings]
        
        print(f"[DEBUG] Найдено договоров: {len(bookings)}")
        
        # Если нет договоров, вернем пустой отчет
        if not booking_ids:
            return jsonify({
                'Период': {
                    'Начало': start_date.strftime('%Y-%m-%d') if start_date else 'Все время',
                    'Конец': end_date.strftime('%Y-%m-%d') if end_date else today.strftime('%Y-%m-%d')
                },
                'Общее_количество_договоров': 0,
                'Общая_выручка_от_услуг': 0,
                'Услуги': []
            })
        
        # Получаем все услуги по выбранным договорам
        booking_services = BookingService.query.filter(BookingService.ID_договора.in_(booking_ids)).all()
        print(f"[DEBUG] Найдено услуг в договорах: {len(booking_services)}")
        
        # Группируем услуги по ID и подсчитываем количество
        services_count = {}
        services_quantity = {}
        services_revenue = {}
        
        for bs in booking_services:
            service_id = bs.ID_услуги
            quantity = float(bs.Количество) if bs.Количество else 1.0
            
            if service_id in services_count:
                services_count[service_id] += 1
                services_quantity[service_id] += quantity
            else:
                services_count[service_id] = 1
                services_quantity[service_id] = quantity
        
        # Получаем информацию о каждой услуге и считаем выручку
        all_services = AdditionalService.query.all()
        service_info = {}
        
        for service in all_services:
            service_id = service.ID_услуги
            service_info[service_id] = {
                'ID_услуги': service_id,
                'Название': service.Название,
                'Стоимость': float(service.Стоимость) if service.Стоимость else 0.0
            }
            
            if service_id in services_quantity:
                cost = service_info[service_id]['Стоимость']
                quantity = services_quantity[service_id]
                services_revenue[service_id] = float(cost) * float(quantity)
            else:
                services_revenue[service_id] = 0.0
        
        # Формируем финальный отчет
        report = []
        
        for service_id in services_count.keys():
            if service_id not in service_info:
                continue
                
            service_data = {
                'ID_услуги': service_id,
                'Название': service_info[service_id]['Название'],
                'Стоимость': service_info[service_id]['Стоимость'],
                'Количество_договоров': services_count[service_id],
                'Общее_количество': services_quantity[service_id],
                'Выручка': services_revenue[service_id]
            }
            
            report.append(service_data)
        
        # Сортируем услуги по популярности (количеству договоров)
        report.sort(key=lambda x: x['Количество_договоров'], reverse=True)
        
        # Формируем итоговую статистику
        summary = {
            'Период': {
                'Начало': start_date.strftime('%Y-%m-%d') if start_date else 'Все время',
                'Конец': end_date.strftime('%Y-%m-%d') if end_date else today.strftime('%Y-%m-%d')
            },
            'Общее_количество_договоров': len(bookings),
            'Общая_выручка_от_услуг': sum(services_revenue.values()),
            'Услуги': report
        }
        
        return jsonify(summary)
    
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при формировании отчета по популярным услугам: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        # Возвращаем пустой отчет с информацией об ошибке, но с корректной структурой
        return jsonify({
            'error': f'Ошибка при формировании отчета: {str(e)}',
            'Период': {
                'Начало': 'Ошибка',
                'Конец': 'Ошибка'
            },
            'Общее_количество_договоров': 0,
            'Общая_выручка_от_услуг': 0,
            'Услуги': []
        }), 500

@bp.route('/api/employee/client_documents/<int:client_id>', methods=['GET'])
@jwt_required()
def get_client_documents(client_id):
    # Проверяем права
    error = employee_required()
    if error:
        return error
        
    try:
        # Получаем данные клиента и его документы
        client = Client.query.get_or_404(client_id)
        passport = Passport.query.filter_by(ID_клиента=client_id).first()
        license = DriversLicense.query.filter_by(ID_клиента=client_id).first()
        
        # Формируем ответ
        documents = {
            'ID_клиента': client.ID_клиента,
            'ФИО': f"{client.Фамилия} {client.Имя_Отчество}",
            'паспорт': None,
            'вод_удостоверение': None
        }
        
        if passport:
            documents['паспорт'] = {
                'ID_клиента': passport.ID_клиента,
                'Серия_Номер': passport.Серия_Номер,
                'Дата_выдачи': passport.Дата_выдачи.strftime('%Y-%m-%d') if passport.Дата_выдачи else None,
                'Срок_действия': passport.Срок_действия.strftime('%Y-%m-%d') if passport.Срок_действия else None,
                'Кем_выдан': passport.Кем_выдан,
                'Код_подразделения': passport.Код_подразделения
            }
            
        if license:
            documents['вод_удостоверение'] = {
                'ID_клиента': license.ID_клиента,
                'Номер': license.Номер,
                'Дата_выдачи': license.Дата_выдачи.strftime('%Y-%m-%d') if license.Дата_выдачи else None,
                'Срок_действия': license.Срок_действия.strftime('%Y-%m-%d') if license.Срок_действия else None,
                'Место_выдачи': license.Место_выдачи
            }
            
        return jsonify(documents)
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при получении документов клиента: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении документов клиента'}), 500

# Маршрут для получения услуг
@bp.route('/api/employee/services', methods=['GET'])
@jwt_required()
def get_employee_services():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        services = AdditionalService.query.all()
        result = []
        
        for service in services:
            service_data = {
                'ID_услуги': service.ID_услуги,
                'Название': service.Название,
                'Стоимость': float(service.Стоимость) if service.Стоимость else 0
            }
            result.append(service_data)
            
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при получении списка услуг: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении списка услуг'}), 500

# Маршрут для получения сотрудников
@bp.route('/api/employee/employees', methods=['GET'])
@jwt_required()
def get_employees():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        employees = Employee.query.all()
        result = []
        
        for employee in employees:
            employee_data = {
                'ID_сотрудника': employee.ID_сотрудника,
                'ФИО_с': employee.ФИО_с,
                'Должность': employee.Должность,
                'Телефон_с': employee.Телефон_с,
                'email': employee.email,
                'Оклад': float(employee.Оклад) if employee.Оклад else 0
            }
            result.append(employee_data)
            
        return jsonify(result)
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при получении списка сотрудников: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при получении списка сотрудников'}), 500

# Маршрут для добавления услуги
@bp.route('/api/employee/add_service', methods=['POST'])
@jwt_required()
def add_service():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    data = request.get_json()
    if not data or 'Название' not in data or 'Стоимость' not in data:
        return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
    
    try:
        # Создаем новую услугу
        service = AdditionalService(
            Название=data['Название'],
            Стоимость=data['Стоимость']
        )
        
        db.session.add(service)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Услуга успешно добавлена',
            'service': {
                'ID_услуги': service.ID_услуги,
                'Название': service.Название,
                'Стоимость': float(service.Стоимость) if service.Стоимость else 0
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении услуги: {str(e)}")
        return jsonify({'error': 'Ошибка при добавлении услуги'}), 500

# Маршрут для добавления сотрудника
@bp.route('/api/employee/add_employee', methods=['POST'])
@jwt_required()
def add_employee():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    data = request.get_json()
    required_fields = ['ФИО_с', 'Должность', 'email', 'Пароль']
    
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Отсутствует обязательное поле: {field}'}), 400
    
    try:
        # Проверяем, не занят ли email
        if Employee.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email уже используется'}), 400
        
        # Создаем нового сотрудника
        employee = Employee(
            ФИО_с=data['ФИО_с'],
            Должность=data['Должность'],
            Телефон_с=data.get('Телефон_с', ''),
            Оклад=data.get('Оклад', 0),
            email=data['email'],
            Пароль=data['Пароль']
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Сотрудник успешно добавлен',
            'employee': {
                'ID_сотрудника': employee.ID_сотрудника,
                'ФИО_с': employee.ФИО_с,
                'Должность': employee.Должность
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при добавлении сотрудника: {str(e)}")
        return jsonify({'error': 'Ошибка при добавлении сотрудника'}), 500

# Маршрут для обновления стоимости услуги
@bp.route('/api/employee/update_service_price', methods=['POST'])
@jwt_required()
def update_service_price():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        if not data or 'ID_услуги' not in data or 'Стоимость' not in data:
            return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
            
        service_id = data['ID_услуги']
        new_price = data['Стоимость']
        
        # Находим услугу в базе данных
        service = AdditionalService.query.get(service_id)
        if not service:
            return jsonify({'error': 'Услуга не найдена'}), 404
            
        # Обновляем стоимость
        service.Стоимость = new_price
        db.session.commit()
        
        print(f"[DEBUG] Стоимость услуги ID={service_id} обновлена на '{new_price}'")
        return jsonify({'message': 'Стоимость услуги успешно обновлена'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при обновлении стоимости услуги: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при обновлении стоимости услуги'}), 500

# Маршрут для обновления оклада сотрудника
@bp.route('/api/employee/update_employee_salary', methods=['POST'])
@jwt_required()
def update_employee_salary():
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        data = request.get_json()
        
        if not data or 'ID_сотрудника' not in data or 'Оклад' not in data:
            return jsonify({'error': 'Отсутствуют необходимые данные'}), 400
            
        employee_id = data['ID_сотрудника']
        new_salary = data['Оклад']
        
        # Находим сотрудника в базе данных
        employee = Employee.query.get(employee_id)
        if not employee:
            return jsonify({'error': 'Сотрудник не найден'}), 404
            
        # Обновляем оклад
        employee.Оклад = new_salary
        db.session.commit()
        
        print(f"[DEBUG] Оклад сотрудника ID={employee_id} обновлен на '{new_salary}'")
        return jsonify({'message': 'Оклад сотрудника успешно обновлен'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при обновлении оклада сотрудника: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при обновлении оклада сотрудника'}), 500

# Маршрут для удаления автомобиля
@bp.route('/api/employee/delete_car/<int:car_id>', methods=['DELETE'])
@jwt_required()
def delete_car(car_id):
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Находим автомобиль
        car = Car.query.get_or_404(car_id)
        
        # Проверяем, не используется ли автомобиль в активных договорах
        active_bookings = Booking.query.filter_by(ID_автомобиля=car_id, Статус_договора='Активен').first()
        if active_bookings:
            return jsonify({'error': 'Невозможно удалить автомобиль, он используется в активных договорах'}), 400
            
        # Удаляем автомобиль
        db.session.delete(car)
        db.session.commit()
        
        return jsonify({'message': 'Автомобиль успешно удален'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при удалении автомобиля: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при удалении автомобиля'}), 500

# Маршрут для удаления услуги
@bp.route('/api/employee/delete_service/<int:service_id>', methods=['DELETE'])
@jwt_required()
def delete_service(service_id):
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Находим услугу
        service = AdditionalService.query.get_or_404(service_id)
        
        # Проверяем, не используется ли услуга в активных договорах
        booking_services = BookingService.query.filter_by(ID_услуги=service_id).join(Booking).filter(Booking.Статус_договора == 'Активен').first()
        if booking_services:
            return jsonify({'error': 'Невозможно удалить услугу, она используется в активных договорах'}), 400
            
        # Удаляем связанные записи в таблице BookingService
        BookingService.query.filter_by(ID_услуги=service_id).delete()
        
        # Удаляем услугу
        db.session.delete(service)
        db.session.commit()
        
        return jsonify({'message': 'Услуга успешно удалена'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при удалении услуги: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при удалении услуги'}), 500

# Маршрут для удаления типа штрафа
@bp.route('/api/employee/delete_fine/<int:fine_id>', methods=['DELETE'])
@jwt_required()
def delete_fine(fine_id):
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    try:
        # Находим тип штрафа
        fine = Fine.query.get_or_404(fine_id)
        
        # Проверяем, не используется ли тип штрафа в активных договорах
        booking_fines = BookingFine.query.filter_by(ID_штрафа=fine_id).join(Booking).filter(Booking.Статус_договора == 'Активен').first()
        if booking_fines:
            return jsonify({'error': 'Невозможно удалить тип штрафа, он используется в активных договорах'}), 400
            
        # Удаляем связанные записи в таблице BookingFine
        BookingFine.query.filter_by(ID_штрафа=fine_id).delete()
        
        # Удаляем тип штрафа
        db.session.delete(fine)
        db.session.commit()
        
        return jsonify({'message': 'Тип штрафа успешно удален'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при удалении типа штрафа: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при удалении типа штрафа'}), 500

# Маршрут для удаления сотрудника
@bp.route('/api/employee/delete_employee/<int:employee_id>', methods=['DELETE'])
@jwt_required()
def delete_employee(employee_id):
    # Проверяем права
    error = employee_required()
    if error:
        return error
    
    # Проверяем, что сотрудник не удаляет сам себя
    current_employee_id = int(get_jwt_identity())
    if current_employee_id == employee_id:
        return jsonify({'error': 'Невозможно удалить собственную учетную запись'}), 400
    
    try:
        # Находим сотрудника
        employee = Employee.query.get_or_404(employee_id)
        
        # Проверяем, не привязаны ли к сотруднику активные договоры
        active_bookings = Booking.query.filter_by(ID_сотрудника=employee_id, Статус_договора='Активен').first()
        if active_bookings:
            return jsonify({'error': 'Невозможно удалить сотрудника, у него есть активные договоры'}), 400
            
        # Удаляем сотрудника
        db.session.delete(employee)
        db.session.commit()
        
        return jsonify({'message': 'Сотрудник успешно удален'}), 200
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при удалении сотрудника: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при удалении сотрудника'}), 500

@bp.route('/api/employee/reports/insurances', methods=['GET'])
@jwt_required()
def get_insurances_report():
    # Проверяем права
    error = employee_required()
    if error:
        return error
        
    try:
        # Получаем параметры запроса
        insurance_type = request.args.get('type')
        max_coverage = request.args.get('max_coverage')
        status = request.args.get('status')
        price_sort = request.args.get('price_sort')
        
        # Базовый запрос
        query = db.session.query(
            Insurance,
            Car.Марка,
            Car.Модель
        ).join(Car, Insurance.ID_автомобиля == Car.ID_автомобиля)
        
        # Применяем фильтры
        if insurance_type:
            query = query.filter(Insurance.Тип_страховки == insurance_type)
            
        if max_coverage:
            query = query.filter(Insurance.МаксСумма_покрытия <= float(max_coverage))
            
        if status == 'active':
            query = query.filter(Insurance.Дата_окончания >= datetime.now().date())
        elif status == 'expired':
            query = query.filter(Insurance.Дата_окончания < datetime.now().date())
            
        # Применяем сортировку по стоимости
        if price_sort == 'asc':
            query = query.order_by(Insurance.Стоимость.asc())
        elif price_sort == 'desc':
            query = query.order_by(Insurance.Стоимость.desc())
            
        # Выполняем запрос
        results = query.all()
        
        # Преобразуем результаты
        insurances = []
        for insurance, марка, модель in results:
            insurances.append({
                'ID_страховки': insurance.ID_страховки,
                'Автомобиль': f"{марка} {модель}",
                'Тип_страховки': insurance.Тип_страховки,
                'Максимум_покрытия': float(insurance.МаксСумма_покрытия) if insurance.МаксСумма_покрытия else 0,
                'Номер_полиса': insurance.Номер_полиса,
                'Дата_начала': insurance.Дата_начала.strftime('%Y-%m-%d'),
                'Дата_окончания': insurance.Дата_окончания.strftime('%Y-%m-%d'),
                'Стоимость': float(insurance.Стоимость) if insurance.Стоимость else 0,
                'Просрочена': insurance.Дата_окончания < datetime.now().date()
            })
            
        return jsonify(insurances)
    except Exception as e:
        import traceback
        print(f"[ОШИБКА] Исключение при получении отчета по страховкам: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при формировании отчета по страховкам'}), 500

@bp.route('/api/employee/update_payment_status', methods=['POST'])
@jwt_required()
def update_payment_status():
    # Проверяем права
    error = employee_required()
    if error:
        return error
        
    try:
        data = request.get_json()
        contract_id = data.get('ID_договора')
        new_status = data.get('Статус_оплаты')
        
        # Находим запись об оплате для данного договора
        payment = Payment.query.filter_by(ID_договора=contract_id).first()
        
        if payment:
            # Обновляем статус существующей оплаты
            payment.Статус_оплаты = new_status
            payment.Дата_оплаты = datetime.now().date() if new_status == 'Оплачено' else None
        else:
            # Создаем новую запись об оплате, если не существует
            payment = Payment(
                ID_договора=contract_id,
                Статус_оплаты=new_status,
                Дата_оплаты=datetime.now().date() if new_status == 'Оплачено' else None,
                Способ_оплаты='Карта'  # По умолчанию
            )
            db.session.add(payment)
            
        db.session.commit()
        return jsonify({'message': 'Статус оплаты успешно обновлен'})
    except Exception as e:
        db.session.rollback()
        import traceback
        print(f"[ОШИБКА] Исключение при обновлении статуса оплаты: {str(e)}")
        print(f"[ОШИБКА] Трассировка: {traceback.format_exc()}")
        return jsonify({'error': 'Ошибка при обновлении статуса оплаты'}), 500