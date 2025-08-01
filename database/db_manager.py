from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from database.models import Base
import os
from typing import Optional

class DatabaseManager:
    """Менеджер для работы с SQLite базой данных"""
    
    def __init__(self, db_path: str = "observer.db"):
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        
    def init_database(self):
        """Инициализация базы данных"""
        try:
            # Создаём движок SQLAlchemy для SQLite
            self.engine = create_engine(f"sqlite:///{self.db_path}")
            
            # Создаём все таблицы
            Base.metadata.create_all(bind=self.engine)
            
            # Создаём фабрику сессий
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            print(f"✅ База данных инициализирована: {self.db_path}")
            return True
            
        except SQLAlchemyError as e:
            print(f"❌ Ошибка инициализации БД: {e}")
            return False
    
    def get_session(self) -> Session:
        """Получить сессию базы данных"""
        if not self.SessionLocal:
            raise Exception("База данных не инициализирована. Вызовите init_database()")
        return self.SessionLocal()
    
    def close_session(self, session: Session):
        """Закрыть сессию"""
        session.close()
    
    def test_connection(self) -> bool:
        """Тест подключения к базе данных"""
        try:
            session = self.get_session()
            from sqlalchemy import text
            session.execute(text("SELECT 1"))
            session.close()
            print("✅ Подключение к базе данных успешно")
            return True
        except Exception as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            return False
    
    def get_database_info(self):
        """Получить информацию о базе данных"""
        if not os.path.exists(self.db_path):
            return {"status": "База данных не создана"}
        
        file_size = os.path.getsize(self.db_path)
        return {
            "path": self.db_path,
            "size_mb": round(file_size / 1024 / 1024, 2),
            "exists": True
        }

# Глобальный экземпляр менеджера БД
db_manager = DatabaseManager()

def init_db():
    """Инициализация базы данных (для использования в main.py)"""
    return db_manager.init_database()

def get_db_session():
    """Получить сессию БД (для использования в других модулях)"""
    return db_manager.get_session() 