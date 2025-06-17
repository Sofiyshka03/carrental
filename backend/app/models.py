from datetime import datetime
from . import db
from sqlalchemy import Numeric

class Client(db.Model):
    __tablename__ = 'Клиенты'
    ID_клиента = db.Column(db.Integer, primary_key=True)
    Фамилия = db.Column(db.String(100), nullable=False)
    Имя_Отчество = db.Column(db.String(100), nullable=False)
    Пол = db.Column(db.String(1))
    Дата_рождения = db.Column(db.Date)
    email = db.Column(db.String(120), unique=True)
    Пароль = db.Column(db.String(200))
    телефоны = db.relationship('PhoneNumber', backref='client', lazy=True)
    паспорт = db.relationship('Passport', backref='client', uselist=False)
    вод_удостоверение = db.relationship('DriversLicense', backref='client', uselist=False)

class PhoneNumber(db.Model):
    __tablename__ = 'Телефон_клиента'
    ID_телефона = db.Column(db.Integer, primary_key=True)
    Номер = db.Column(db.String(20), nullable=False)
    Тип = db.Column(db.String(20))
    ID_клиента = db.Column(db.Integer, db.ForeignKey('Клиенты.ID_клиента'))

class Passport(db.Model):
    __tablename__ = 'Паспорт_клиента'
    ID_клиента = db.Column(db.Integer, db.ForeignKey('Клиенты.ID_клиента'), primary_key=True)
    Серия_Номер = db.Column(db.String(20), nullable=False)
    Дата_выдачи = db.Column(db.Date, nullable=False)
    Срок_действия = db.Column(db.Date)
    Кем_выдан = db.Column(db.String(200))
    Код_подразделения = db.Column(db.String(20))

class DriversLicense(db.Model):
    __tablename__ = 'Водительское_удостоверение'
    ID_клиента = db.Column(db.Integer, db.ForeignKey('Клиенты.ID_клиента'), primary_key=True)
    Номер = db.Column(db.String(20), nullable=False)
    Дата_выдачи = db.Column(db.Date, nullable=False)
    Срок_действия = db.Column(db.Date, nullable=False)
    Место_выдачи = db.Column(db.String(200))
    ID_сотрудника = db.Column(db.Integer, db.ForeignKey('Сотрудники.ID_сотрудника'))

class Employee(db.Model):
    __tablename__ = 'Сотрудники'
    ID_сотрудника = db.Column(db.Integer, primary_key=True)
    ФИО_с = db.Column(db.String(100), nullable=False)
    Должность = db.Column(db.String(50), nullable=False)
    Телефон_с = db.Column(db.String(20))
    Оклад = db.Column(Numeric(10, 2))
    email = db.Column(db.String(120), unique=True)
    Пароль = db.Column(db.String(200))
    
    # Связь с договорами
    договоры = db.relationship('Booking', backref='employee', lazy=True, foreign_keys='Booking.ID_сотрудника')

class Car(db.Model):
    __tablename__ = 'Автопарк'
    ID_автомобиля = db.Column(db.Integer, primary_key=True)
    Марка = db.Column(db.String(50), nullable=False)
    Модель = db.Column(db.String(50), nullable=False)
    Год_выпуска = db.Column(db.Integer)
    Категория = db.Column(db.String(50))
    Стоимость = db.Column(Numeric(10, 2))
    Статус_авто = db.Column(db.String(20))
    image = db.Column(db.String(255))  # Добавляем поле для хранения пути к изображению
    Дата_техосмотра = db.Column(db.Date)

class Booking(db.Model):
    __tablename__ = 'Договоры'
    ID_договора = db.Column(db.Integer, primary_key=True)
    Дата_начала = db.Column(db.Date, nullable=False)
    Дата_окончания = db.Column(db.Date, nullable=False)
    Статус_договора = db.Column(db.String(20))
    Стоимость = db.Column(Numeric(10, 2))
    ID_клиента = db.Column(db.Integer, db.ForeignKey('Клиенты.ID_клиента'))
    ID_автомобиля = db.Column(db.Integer, db.ForeignKey('Автопарк.ID_автомобиля'))
    ID_сотрудника = db.Column(db.Integer, db.ForeignKey('Сотрудники.ID_сотрудника'))
    
    # Связи
    car = db.relationship('Car', backref='bookings')
    штрафы = db.relationship('BookingFine', backref='booking', lazy=True)

class AdditionalService(db.Model):
    __tablename__ = 'Дополнительные_услуги'
    ID_услуги = db.Column(db.Integer, primary_key=True)
    Название = db.Column(db.String(50), nullable=False)
    Стоимость = db.Column(Numeric(10, 2))

class BookingService(db.Model):
    __tablename__ = 'Договоры_Дополнительные_услуги'
    ID_договора = db.Column(db.Integer, db.ForeignKey('Договоры.ID_договора'), primary_key=True)
    ID_услуги = db.Column(db.Integer, db.ForeignKey('Дополнительные_услуги.ID_услуги'), primary_key=True)
    Количество = db.Column(db.Integer, default=1)

class Fine(db.Model):
    __tablename__ = 'Штрафы'
    ID_штрафа = db.Column(db.Integer, primary_key=True)
    Название = db.Column(db.String(100), nullable=False)
    Стоимость = db.Column(Numeric(10, 2), nullable=False)
    
    # Связь с договорами
    договоры = db.relationship('BookingFine', backref='fine', lazy=True)
    
    def to_dict(self):
        return {
            'ID_штрафа': self.ID_штрафа,
            'Название': self.Название,
            'Стоимость': float(self.Стоимость) if self.Стоимость else 0
        }

class BookingFine(db.Model):
    __tablename__ = 'Договоры_Штрафы'
    ID_договора = db.Column(db.Integer, db.ForeignKey('Договоры.ID_договора'), primary_key=True)
    ID_штрафа = db.Column(db.Integer, db.ForeignKey('Штрафы.ID_штрафа'), primary_key=True)
    Количество = db.Column(db.Integer, default=1)

    def to_dict(self):
        return {
            'ID_договора': self.ID_договора,
            'ID_штрафа': self.ID_штрафа,
            'Количество': self.Количество
        }

class Payment(db.Model):
    __tablename__ = 'Оплата'
    ID_оплаты = db.Column(db.Integer, primary_key=True)
    Дата_оплаты = db.Column(db.Date)
    Статус_оплаты = db.Column(db.String(20))  # Оплачено, В ожидании, Отклонено
    ID_договора = db.Column(db.Integer, db.ForeignKey('Договоры.ID_договора'))
    Способ_оплаты = db.Column(db.String(20))  # Карта, Наличные 

class Insurance(db.Model):
    __tablename__ = 'Страховки'
    ID_страховки = db.Column(db.Integer, primary_key=True)
    Тип_страховки = db.Column(db.String(50), nullable=False)  # ОСАГО, КАСКО, Другое
    МаксСумма_покрытия = db.Column(Numeric(15, 2))  # Максимальная сумма страхового покрытия
    Дата_начала = db.Column(db.Date, nullable=False)
    Дата_окончания = db.Column(db.Date, nullable=False)
    Стоимость = db.Column(Numeric(10, 2))
    Номер_полиса = db.Column(db.String(50))
    ID_автомобиля = db.Column(db.Integer, db.ForeignKey('Автопарк.ID_автомобиля'))
    
    # Связь с автомобилем
    автомобиль = db.relationship('Car', backref='страховки') 