// Observer - Основной JavaScript файл

document.addEventListener('DOMContentLoaded', function() {
    console.log('Observer загружен!');
    
    // Инициализация всех компонентов
    initAlerts();
    initModals();
    initForms();
    initTables();
});

// Управление алертами
function initAlerts() {
    // Автоматическое скрытие алертов через 5 секунд
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            if (alert.classList.contains('show')) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    });
}

// Управление модальными окнами
function initModals() {
    // Обработка модальных окон
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function(event) {
            console.log('Модальное окно открыто:', modal.id);
        });
    });
}

// Управление формами
function initForms() {
    // Валидация форм
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

// Управление таблицами
function initTables() {
    // Поиск в таблицах
    const searchInputs = document.querySelectorAll('.table-search');
    searchInputs.forEach(input => {
        input.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table');
            const rows = table.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    });
}

// Функции для работы с API
const API = {
    // Получить список доменов
    async getDomains() {
        try {
            const response = await fetch('/api/domains');
            return await response.json();
        } catch (error) {
            console.error('Ошибка получения доменов:', error);
            return [];
        }
    },
    
    // Добавить домен
    async addDomain(name, displayName) {
        try {
            const response = await fetch('/api/domains', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `name=${encodeURIComponent(name)}&display_name=${encodeURIComponent(displayName)}`
            });
            return await response.json();
        } catch (error) {
            console.error('Ошибка добавления домена:', error);
            throw error;
        }
    },
    
    // Получить снимки домена
    async getSnapshots(domainId) {
        try {
            const response = await fetch(`/api/snapshots/${domainId}`);
            return await response.json();
        } catch (error) {
            console.error('Ошибка получения снимков:', error);
            return [];
        }
    },
    
    // Проверить статус системы
    async getHealth() {
        try {
            const response = await fetch('/health');
            return await response.json();
        } catch (error) {
            console.error('Ошибка проверки статуса:', error);
            return { status: 'error' };
        }
    }
};

// Утилиты
const Utils = {
    // Форматирование даты
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    },
    
    // Форматирование размера файла
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Б';
        const k = 1024;
        const sizes = ['Б', 'КБ', 'МБ', 'ГБ'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    // Показать уведомление
    showNotification(message, type = 'success') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        // Автоматическое скрытие через 5 секунд
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },
    
    // Показать загрузку
    showLoading(element) {
        element.innerHTML = '<div class="loading"></div>';
        element.disabled = true;
    },
    
    // Скрыть загрузку
    hideLoading(element, originalText) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
};

// Экспорт для использования в других файлах
window.Observer = {
    API,
    Utils
}; 