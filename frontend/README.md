# Frontend (React + Vite + TypeScript)

Это SPA на React/TypeScript для проекта GHOST.
В будущем здесь появится визуальный конструктор отчётов с блоками, проверками и экспортом.
Сейчас реализована только базовая заглушка интерфейса.

## Требования

- Node.js 18+ (LTS рекомендуется)
- npm

## Установка зависимостей

```bash
cd frontend
npm install
```

## Запуск в режиме разработки

```bash
cd frontend
npm run dev
```

- Приложение будет доступно по адресу, который покажет Vite (обычно `http://localhost:5173`).

## Сборка в production-режиме

```bash
cd frontend
npm run build
npm run preview
```

## Требования и спецификация

Полный список функциональных и технических требований к проекту находится в корневом файле
[`REQUIREMENTS.md`](../REQUIREMENTS.md).

## Проверка кода и форматирование

Для проверки кода используется ESLint, для автоформатирования — Prettier.

```bash
cd frontend
npm install
```

Запуск линтера:

```bash
cd frontend
npm run lint
```

Автоформатирование кода:

```bash
cd frontend
npm run format
```
