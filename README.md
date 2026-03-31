# Лабораторная работа №11 — задание 1

Это готовый проект **SocialEng Detector** на Python по требованиям лабораторной работы №11: анализ сообщений на признаки социальной инженерии с консольным и веб-режимом, SQLite-историей, ML-моделью, PDF-экспортом и unit-тестами.

## Что реализовано

- ввод `sender`, `subject`, `body`
- многоуровневый анализ:
  - эвристики: urgency, fear, authority, greed, reciprocity, scarcity
  - статистика: `!`, доля CAPS, ссылки, подозрительные домены
  - ML-модель `LogisticRegression` на синтетическом датасете
- синтетический датасет на **300 примеров**
- подробный отчёт: риск 0–100, техники, объяснения, рекомендации
- веб-интерфейс на **FastAPI**
- сохранение истории анализов в **SQLite**
- экспорт отчёта в **PDF**
- unit-тесты
- запуск через **Docker**

## Структура проекта

- `app.py` — веб-приложение и CLI
- `detector.py` — логика анализа
- `data_factory.py` — генерация синтетического датасета
- `ml_model.py` — обучение и загрузка модели
- `storage.py` — работа с SQLite
- `templates/` — HTML-шаблоны
- `static/` — стили
- `tests/` — unit-тесты
- `data/` — CSV, модель и база SQLite

## Установка

```bash
pip install -r requirements.txt
python data_factory.py
python ml_model.py
```

## Запуск веб-версии

```bash
python app.py --mode web --host 127.0.0.1 --port 8000
```

Открыть в браузере:

```bash
http://127.0.0.1:8000
```

## Запуск консольной версии

```bash
python app.py --mode cli \
  --sender "security-alert@verify-now.help" \
  --subject "СРОЧНО: подтвердите аккаунт" \
  --body "Немедленно перейдите по ссылке http://verify-account-now.xyz/login иначе доступ будет заблокирован!!!"
```

## Тесты

```bash
python -m unittest discover -s tests
```

## Docker

```bash
docker build -t socialeng-detector .
docker run -p 8000:8000 socialeng-detector
```

## Примечание по безопасности

Проект использует только **синтетические данные** и предназначен для локального запуска.
