from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .models import Booking, db
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('contract_status_updater')

def update_expired_contracts():
    """
    Автоматически меняет статус договоров с 'Активен' на 'Завершен',
    если срок аренды истек (текущая дата > даты окончания).
    """
    try:
        today = datetime.now().date()
        logger.info(f"[{today}] Запущена проверка истекших договоров аренды")
        
        # Находим все активные договоры с истекшим сроком
        expired_contracts = Booking.query.filter(
            Booking.Дата_окончания < today,
            Booking.Статус_договора == 'Активен'
        ).all()
        
        count = len(expired_contracts)
        logger.info(f"Найдено {count} истекших активных договоров")
        
        # Обновляем статусы найденных договоров
        for contract in expired_contracts:
            contract.Статус_договора = 'Завершен'
            logger.info(f"Договор #{contract.ID_договора} помечен как завершенный (истек {contract.Дата_окончания})")
        
        # Сохраняем изменения в базе данных
        if count > 0:
            db.session.commit()
            logger.info(f"Успешно обновлены статусы {count} договоров")
        
        return count
    except Exception as e:
        db.session.rollback()
        logger.error(f"Ошибка при обновлении статусов договоров: {str(e)}")
        return 0

def start_scheduler(app):
    """
    Запускает планировщик задач для автоматического обновления статусов договоров.
    Задача будет выполняться каждый день в 00:05.
    """
    scheduler = BackgroundScheduler()
    
    # Регистрируем задачу в планировщике (выполнение каждый день в 00:05)
    scheduler.add_job(
        func=update_expired_contracts,
        trigger='cron',
        hour=0,
        minute=5,
        id='update_contract_status_job'
    )
    
    # Также запускаем проверку сразу при старте сервера
    with app.app_context():
        updated_count = update_expired_contracts()
        logger.info(f"При старте сервера обновлены статусы {updated_count} договоров")
    
    # Запускаем планировщик
    scheduler.start()
    logger.info("Планировщик задач запущен успешно")
    
    return scheduler 