VENV_NAME=venv

# Путь к файлу manage.py
DJANGO_MANAGE=manage.py

# Пакеты для установки
REQUIREMENTS=requirements.txt

# Команды для работы с Django-проектом

install: 
	@echo "Installing dependencies..."
	@pip install -r $(REQUIREMENTS)

# Создать виртуальное окружение
venv: 
	@echo "Creating virtual environment..."
	@python3 -m venv $(VENV_NAME)

# Активировать виртуальное окружение (для Windows и Linux)
activate:
	@echo "Activate the virtual environment using one of the following commands:"
	@echo "For Linux/Mac: source venv/bin/activate"
	@echo "For Windows: .\\venv\\Scripts\\activate"

# Миграции базы данных
migrate: 
	@echo "Applying migrations..."
	@python $(DJANGO_MANAGE) migrate

# Создать суперпользователя
createsuperuser:
	@echo "Creating superuser..."
	@python $(DJANGO_MANAGE) createsuperuser

# Запустить сервер Django
run:
	@echo "Running server..."
	@python $(DJANGO_MANAGE) runserver

# Запуск тестов
test:
	@echo "Running tests..."
	@python $(DJANGO_MANAGE) test

# Сделать миграции и собрать статику
collectstatic:
	@echo "Collecting static files..."
	@python $(DJANGO_MANAGE) collectstatic --noinput

# Запустить команду shell Django
shell:
	@echo "Opening Django shell..."
	@python $(DJANGO_MANAGE) shell

# Проверка стиля кода с использованием flake8 (если установлен)
lint:
	@echo "Running linter..."
	@flake8 .

# Запуск тестов с использованием pytest (если установлен)
pytest:
	@echo "Running pytest..."
	@pytest

# Очистить pycache файлы
clean:
	@echo "Cleaning pycache..."
	@find . -name "__pycache__" -exec rm -rf {} \;

# Удалить все файлы миграций (вместо полного удаления базы данных)
resetdb:
	@echo "Resetting database..."
	@rm -rf db.sqlite3
	@python $(DJANGO_MANAGE) migrate

# Установить зависимости, создать виртуальное окружение, выполнить миграции
setup: venv install migrate
	@echo "Setup complete."

# Сделать бэкап базы данных
backupdb:
	@echo "Backing up the database..."
	@python $(DJANGO_MANAGE) dumpdata > db_backup.json

# Восстановить базу данных из бэкапа
restoredb:
	@echo "Restoring the database..."
	@python $(DJANGO_MANAGE) loaddata db_backup.json


#Docker
# Переменные
DOCKER_COMPOSE = docker-compose
SERVICE = web

# Запуск контейнеров
up:
	$(DOCKER_COMPOSE) up --build

# Остановка контейнеров
down:
	$(DOCKER_COMPOSE) down

# Перезапуск контейнеров
restart:
	$(DOCKER_COMPOSE) restart

# Остановка и удаление контейнеров и volumes
clean:
	$(DOCKER_COMPOSE) down -v

# Применение миграций
migrate:
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py migrate

# Создание суперпользователя
superuser:
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py createsuperuser

# Запуск тестов
test:
	$(DOCKER_COMPOSE) exec $(SERVICE) python manage.py test

# Просмотр логов
logs:
	$(DOCKER_COMPOSE) logs -f $(SERVICE)

# Запуск bash в контейнере
bash:
	$(DOCKER_COMPOSE) exec $(SERVICE) bash

# Проверка состояния контейнеров
status:
	$(DOCKER_COMPOSE) ps

clean-cache:
	docker system prune -f

up-detached:
	$(DOCKER_COMPOSE) up --build -d