from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from database.db_manager import init_db, get_db_session, db_manager
from database.models import Domain, Snapshot, Change, Report
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uvicorn
from datetime import datetime

app = FastAPI(title="Observer", description="Система мониторинга сайтов конкурентов")

# Подключение статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Инициализация базы данных при запуске
@app.on_event("startup")
async def startup_event():
    """Инициализация при запуске приложения"""
    print("🚀 Запуск Observer...")
    if init_db():
        print("✅ База данных готова к работе")
    else:
        print("❌ Ошибка инициализации базы данных")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Главная страница - Dashboard"""
    try:
        session = get_db_session()
        
        # Получаем статистику
        domains_count = session.query(Domain).count()
        snapshots_count = session.query(Snapshot).count()
        changes_count = session.query(Change).count()
        reports_count = session.query(Report).count()
        
        # Получаем активные домены
        domains = session.query(Domain).filter(Domain.is_active == True).all()
        
        # Получаем последние изменения (пока пустые)
        recent_changes = []
        
        session.close()
        
        stats = {
            "domains_count": domains_count,
            "snapshots_count": snapshots_count,
            "changes_count": changes_count,
            "reports_count": reports_count
        }
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "stats": stats,
            "domains": domains,
            "recent_changes": recent_changes
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки dashboard: {str(e)}")

@app.get("/domains", response_class=HTMLResponse)
async def domains_page(request: Request):
    """Страница управления доменами"""
    try:
        session = get_db_session()
        domains = session.query(Domain).all()
        session.close()
        
        return templates.TemplateResponse("domains.html", {
            "request": request,
            "domains": domains
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки доменов: {str(e)}")

@app.get("/snapshots", response_class=HTMLResponse)
async def snapshots_page(request: Request):
    """Страница снимков"""
    try:
        session = get_db_session()
        domains = session.query(Domain).filter(Domain.is_active == True).all()
        session.close()
        
        return templates.TemplateResponse("snapshots.html", {
            "request": request,
            "domains": domains
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки снимков: {str(e)}")

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """Страница отчётов"""
    try:
        session = get_db_session()
        reports = session.query(Report).order_by(Report.created_at.desc()).all()
        session.close()
        
        return templates.TemplateResponse("reports.html", {
            "request": request,
            "reports": reports
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка загрузки отчётов: {str(e)}")

# API эндпоинты
@app.get("/health")
def health_check():
    """Проверка состояния системы"""
    db_info = db_manager.get_database_info()
    return {
        "status": "healthy",
        "database": db_info,
        "message": "Observer работает корректно"
    }

@app.get("/api/domains", response_model=List[Dict[str, Any]])
def get_domains():
    """Получить список всех доменов"""
    try:
        session = get_db_session()
        domains = session.query(Domain).all()
        result = []
        for domain in domains:
            result.append({
                "id": domain.id,
                "name": domain.name,
                "display_name": domain.display_name,
                "is_active": domain.is_active,
                "created_at": domain.created_at.isoformat() if domain.created_at else None
            })
        session.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения доменов: {str(e)}")

@app.post("/api/domains")
def add_domain(name: str = Form(...), display_name: str = Form(None)):
    """Добавить новый домен для мониторинга"""
    try:
        session = get_db_session()
        
        # Проверяем, не существует ли уже такой домен
        existing = session.query(Domain).filter(Domain.name == name).first()
        if existing:
            session.close()
            raise HTTPException(status_code=400, detail="Домен уже существует")
        
        # Создаём новый домен
        new_domain = Domain(
            name=name,
            display_name=display_name or name
        )
        session.add(new_domain)
        session.commit()
        
        # Получаем ID нового домена
        domain_id = new_domain.id
        session.close()
        
        return {"message": f"Домен {name} добавлен", "domain_id": domain_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка добавления домена: {str(e)}")

@app.get("/api/snapshots/{domain_id}", response_model=List[Dict[str, Any]])
def get_snapshots(domain_id: int):
    """Получить снимки для конкретного домена"""
    try:
        session = get_db_session()
        snapshots = session.query(Snapshot).filter(Snapshot.domain_id == domain_id).order_by(Snapshot.timestamp.desc()).all()
        result = []
        for snapshot in snapshots:
            result.append({
                "id": snapshot.id,
                "timestamp": snapshot.timestamp.isoformat() if snapshot.timestamp else None,
                "status": snapshot.status,
                "page_title": snapshot.page_title,
                "page_url": snapshot.page_url,
                "screenshot_path": snapshot.screenshot_path,
                "html_path": snapshot.html_path,
                "carousel_screenshot_path": snapshot.carousel_screenshot_path
            })
        session.close()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка получения снимков: {str(e)}")

@app.delete("/api/domains/{domain_id}")
def delete_domain(domain_id: int):
    """Удалить домен"""
    try:
        session = get_db_session()
        
        # Находим домен
        domain = session.query(Domain).filter(Domain.id == domain_id).first()
        if not domain:
            session.close()
            raise HTTPException(status_code=404, detail="Домен не найден")
        
        # Проверяем, есть ли связанные снимки
        snapshots_count = session.query(Snapshot).filter(Snapshot.domain_id == domain_id).count()
        if snapshots_count > 0:
            session.close()
            raise HTTPException(status_code=400, detail=f"Нельзя удалить домен с {snapshots_count} снимками. Сначала удалите снимки.")
        
        # Удаляем домен
        domain_name = domain.name
        session.delete(domain)
        session.commit()
        session.close()
        
        return {"message": f"Домен {domain_name} удален"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка удаления домена: {str(e)}")

@app.put("/api/domains/{domain_id}/toggle")
def toggle_domain(domain_id: int):
    """Переключить статус домена (активный/неактивный)"""
    try:
        session = get_db_session()
        
        # Находим домен
        domain = session.query(Domain).filter(Domain.id == domain_id).first()
        if not domain:
            session.close()
            raise HTTPException(status_code=404, detail="Домен не найден")
        
        # Переключаем статус
        domain.is_active = not domain.is_active
        session.commit()
        
        # Получаем обновленный статус
        is_active = domain.is_active
        domain_name = domain.name
        session.close()
        
        status = "активирован" if is_active else "деактивирован"
        return {"message": f"Домен {domain_name} {status}", "is_active": is_active}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка переключения статуса домена: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)