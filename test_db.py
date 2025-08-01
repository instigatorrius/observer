#!/usr/bin/env python3
"""
Скрипт для тестирования базы данных Observer
"""

from database.db_manager import init_db, get_db_session, db_manager
from database.models import Domain, Snapshot
from datetime import datetime

def test_database():
    """Тестирование базы данных"""
    print("🧪 Тестирование базы данных Observer...")
    
    # Инициализация БД
    print("\n1. Инициализация базы данных...")
    if init_db():
        print("✅ База данных создана успешно")
    else:
        print("❌ Ошибка создания базы данных")
        return False
    
    # Тест подключения
    print("\n2. Тест подключения...")
    if db_manager.test_connection():
        print("✅ Подключение работает")
    else:
        print("❌ Ошибка подключения")
        return False
    
    # Информация о БД
    print("\n3. Информация о базе данных...")
    db_info = db_manager.get_database_info()
    print(f"📁 Путь: {db_info.get('path', 'N/A')}")
    print(f"📊 Размер: {db_info.get('size_mb', 0)} МБ")
    
    return True

def add_test_domains():
    """Добавление тестовых доменов"""
    print("\n4. Добавление тестовых доменов...")
    
    test_domains = [
        {"name": "mts.ru", "display_name": "МТС"},
        {"name": "megafon.ru", "display_name": "МегаФон"},
        {"name": "beeline.ru", "display_name": "Билайн"},
        {"name": "tele2.ru", "display_name": "Tele2"}
    ]
    
    session = get_db_session()
    
    for domain_data in test_domains:
        # Проверяем, существует ли уже домен
        existing = session.query(Domain).filter(Domain.name == domain_data["name"]).first()
        if not existing:
            domain = Domain(**domain_data)
            session.add(domain)
            print(f"✅ Добавлен домен: {domain_data['name']}")
        else:
            print(f"ℹ️ Домен уже существует: {domain_data['name']}")
    
    session.commit()
    session.close()
    
    print("✅ Тестовые домены добавлены")

def show_domains():
    """Показать все домены"""
    print("\n5. Список доменов в базе:")
    
    session = get_db_session()
    domains = session.query(Domain).all()
    
    if not domains:
        print("📭 Доменов в базе нет")
    else:
        for domain in domains:
            print(f"  • {domain.name} ({domain.display_name}) - {'активен' if domain.is_active else 'неактивен'}")
    
    session.close()

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестирования Observer Database")
    print("=" * 50)
    
    # Тестируем БД
    if not test_database():
        print("❌ Тестирование не пройдено")
        return
    
    # Добавляем тестовые данные
    add_test_domains()
    
    # Показываем результат
    show_domains()
    
    print("\n" + "=" * 50)
    print("✅ Тестирование завершено успешно!")
    print("💡 Теперь можно запускать main.py")

if __name__ == "__main__":
    main() 