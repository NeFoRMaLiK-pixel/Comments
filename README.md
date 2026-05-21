# Comments SPA (Junior+)

SPA-приложение на Django для древовидных комментариев с валидацией, CAPTCHA, вложениями, AJAX preview и real-time обновлениями.

## Реализация
- Создание комментария с полями:
  - `User Name` (латиница/цифры)
  - `E-mail`
  - `Home page` (опционально)
  - `CAPTCHA`
  - `Text`
- Вложенность (ответы на комментарии, каскадное отображение).
- Сортировка корневых комментариев: `User Name`, `E-mail`, `created_at`, ASC/DESC.
- Пагинация: 25 записей.
- Защита:
  - от SQL-инъекций через ORM и параметризацию DRF;
  - от XSS через whitelist + очистку HTML (`bleach`).
- Разрешены только теги: `<a>`, `<code>`, `<i>`, `<strong>`.
- Проверка корректности закрытия тегов и валидности XHTML-структуры.
- Загрузка вложений:
  - изображения `JPG/GIF/PNG` (авто-уменьшение до 320x240 с сохранением пропорций);
  - текстовый файл `TXT` до 100KB.
- Визуальные эффекты просмотра вложений (lightbox/modal).
- AJAX preview сообщения.
- Панель тегов: `[i]`, `[strong]`, `[code]`, `[a]`.
- WebSocket авто-обновление списка после новых комментариев.

## Структура
- `backend/` — Django-проект
- `db/schema.sql` — SQL-схема БД (можно открыть в MySQL Workbench через SQL import)
- `docker-compose.yml` — web + worker + db + redis

## API
- `GET /api/comments/` — список корневых комментариев (nested replies)
  - query: `ordering` (`username`, `-username`, `email`, `-email`, `created_at`, `-created_at`), `page`
- `POST /api/comments/` — создание комментария (multipart)
- `GET /api/comments/captcha/` — получить CAPTCHA
- `POST /api/comments/preview/` — preview очищенного текста
- `POST /api/auth/token/` — JWT token pair
- `POST /api/auth/token/refresh/` — JWT refresh
- `WS /ws/comments/` — real-time канал

## Быстрый старт (Docker)
1. Скопируйте env:
   - `copy .env.example .env`
2. Запустите сервисы:
   - `docker compose up --build`
3. Откройте:
   - `http://localhost:8000`

Примечание: `web` и `worker` запускаются только после готовности `PostgreSQL` и `Redis` (healthcheck + depends_on conditions), чтобы избежать race-condition на первом старте.

## Локальный запуск без Docker
1. Создайте виртуальное окружение и установите зависимости из `backend/requirements.txt`.
2. Установите переменные окружения (можно из `.env.example`).
3. Выполните:
   - `python manage.py migrate`
   - `python manage.py runserver`

## Тесты
- `python manage.py test`

