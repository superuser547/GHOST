# Backend (FastAPI)

Это серверная часть проекта GHOST, реализованная на FastAPI.
В дальнейшем backend будет отвечать за генерацию отчётов по ГОСТ/МИСИС и работу с данными.
Сейчас реализован только минимальный healthcheck-эндпоинт.

## Требования к окружению

- Python 3.11+
- Установленный `pip`

## Установка зависимостей

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

## Запуск сервера разработки

После активации виртуального окружения:

```bash
uvicorn app.main:app --reload --port 8000
```

- Приложение будет доступно по адресу `http://localhost:8000/health`.
- Swagger-документация появится по адресу `http://localhost:8000/docs`.

## Требования и спецификация

Подробное функциональное и техническое описание проекта см. в корневом файле [REQUIREMENTS.md](../REQUIREMENTS.md).

## Проверка кода и форматирование

Для разработки рекомендуется использовать `black` и `ruff`.

Установка dev-зависимостей:

```bash
cd backend
# виртуальное окружение уже должно быть активировано
pip install -r requirements-dev.txt
```

Запуск форматтера:

```bash
cd backend
black app
```

Запуск линтера:

```bash
cd backend
ruff check app
```
