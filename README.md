# Система аренды автомобилей

Веб-приложение для управления арендой автомобилей с личным кабинетом сотрудников.

## Технологии

### Backend
- **Flask** - веб-фреймворк
- **Flask-SQLAlchemy** - ORM для работы с базой данных
- **Flask-CORS** - поддержка CORS
- **Flask-JWT-Extended** - аутентификация через JWT токены
- **pyodbc** - драйвер для подключения к SQL Server
- **APScheduler** - планировщик задач

### Frontend
- **Vue.js 3** - прогрессивный JavaScript фреймворк
- **Vue Router** - маршрутизация
- **Vuex** - управление состоянием
- **Axios** - HTTP клиент

### База данных
- **SQL Server** - основная база данных

## Установка и запуск

### Предварительные требования

1. **Python 3.8+**
2. **Node.js 14+**
3. **SQL Server** с базой данных Automobiles
4. **SQL Server ODBC Driver**

### Backend

1. Перейдите в папку backend:
```bash
cd backend
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
```

3. Активируйте виртуальное окружение:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. Установите зависимости:
```bash
pip install -r requirements.txt
```

5. Настройте подключение к базе данных в `app/__init__.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc:///?odbc_connect=DRIVER={SQL Server};SERVER=YOUR_SERVER;DATABASE=Automobiles;Trusted_Connection=yes;charset=utf8'
```

6. Запустите сервер:
```bash
python run.py
```

Сервер будет доступен по адресу: http://localhost:5000

### Frontend

1. Перейдите в папку frontend:
```bash
cd frontend
```

2. Установите зависимости:
```bash
npm install
```

3. Запустите сервер разработки:
```bash
npm run serve
```

Приложение будет доступно по адресу: http://localhost:8080

## Функциональность

### Для клиентов
- Просмотр доступных автомобилей
- Бронирование автомобилей
- Просмотр истории бронирований
- Регистрация и авторизация

### Для сотрудников
- Личный кабинет сотрудника
- Добавление штрафов клиентам
- Управление автомобилями (добавление, редактирование)
- Генерация отчетов
- Просмотр всех договоров аренды

## API Endpoints

### Аутентификация
- `POST /api/auth/register` - регистрация клиента
- `POST /api/auth/login` - вход клиента
- `POST /api/auth/employee/login` - вход сотрудника

### Автомобили
- `GET /api/cars` - список всех автомобилей
- `GET /api/cars/<id>` - информация об автомобиле
- `POST /api/cars` - добавление автомобиля (сотрудники)
- `PUT /api/cars/<id>` - обновление автомобиля (сотрудники)

### Бронирования
- `GET /api/bookings` - список бронирований
- `POST /api/bookings` - создание бронирования
- `PUT /api/bookings/<id>` - обновление бронирования

### Штрафы
- `GET /api/fines` - список штрафов
- `POST /api/fines` - добавление штрафа (сотрудники)

### Отчеты
- `GET /api/reports/rental` - отчет по аренде
- `GET /api/reports/fines` - отчет по штрафам

## Структура проекта

Подробная структура проекта описана в файле [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

## Разработка

### Добавление новых функций

1. Создайте модель в `backend/app/models.py`
2. Добавьте маршруты в `backend/app/routes.py`
3. Создайте компоненты Vue в `frontend/src/components/`
4. Добавьте страницы в `frontend/src/views/`
5. Обновите маршрутизацию в `frontend/src/router/index.js`

### Планировщик задач

Система автоматически обновляет статусы договоров аренды каждый день в 00:05. Планировщик запускается при старте сервера.

## Лицензия

MIT License 