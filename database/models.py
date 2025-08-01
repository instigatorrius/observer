from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Domain(Base):
    """Таблица доменов для мониторинга"""
    __tablename__ = 'domains'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)  # например, 'mts.ru'
    display_name = Column(String(255), nullable=True)  # например, 'МТС'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связь с снимками
    snapshots = relationship("Snapshot", back_populates="domain")

class Snapshot(Base):
    """Таблица снимков сайтов"""
    __tablename__ = 'snapshots'
    
    id = Column(Integer, primary_key=True)
    domain_id = Column(Integer, ForeignKey('domains.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Пути к файлам
    screenshot_path = Column(String(500), nullable=True)  # путь к скриншоту
    html_path = Column(String(500), nullable=True)  # путь к HTML-снимку
    carousel_screenshot_path = Column(String(500), nullable=True)  # путь к скриншоту карусели
    
    # Статус обработки
    status = Column(String(50), default='captured')  # captured, processed, error
    
    # Метаданные
    page_title = Column(String(500), nullable=True)
    page_url = Column(String(1000), nullable=True)
    
    # Связи
    domain = relationship("Domain", back_populates="snapshots")
    changes_as_old = relationship("Change", foreign_keys="Change.snapshot_id_old", back_populates="old_snapshot")
    changes_as_new = relationship("Change", foreign_keys="Change.snapshot_id_new", back_populates="new_snapshot")

class Change(Base):
    """Таблица изменений между снимками"""
    __tablename__ = 'changes'
    
    id = Column(Integer, primary_key=True)
    snapshot_id_old = Column(Integer, ForeignKey('snapshots.id'), nullable=False)
    snapshot_id_new = Column(Integer, ForeignKey('snapshots.id'), nullable=False)
    
    # Тип изменения
    change_type = Column(String(100), nullable=False)  # 'content', 'visual', 'structure', 'carousel'
    
    # Описание изменения
    description = Column(Text, nullable=True)
    
    # Детали изменений (JSON)
    diff_data = Column(JSON, nullable=True)  # детальная информация об изменениях
    
    # Время создания
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    old_snapshot = relationship("Snapshot", foreign_keys=[snapshot_id_old], back_populates="changes_as_old")
    new_snapshot = relationship("Snapshot", foreign_keys=[snapshot_id_new], back_populates="changes_as_new")

class Report(Base):
    """Таблица отчётов"""
    __tablename__ = 'reports'
    
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Путь к файлу отчёта
    report_path = Column(String(500), nullable=True)
    
    # Краткое описание
    summary = Column(Text, nullable=True)
    
    # Период отчёта
    date_from = Column(DateTime, nullable=True)
    date_to = Column(DateTime, nullable=True)
    
    # Статус
    status = Column(String(50), default='generated')  # generated, error 