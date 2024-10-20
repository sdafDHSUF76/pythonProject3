
# ДЗ #2
1. Запустить проект с postgresql в докере
2. Расширить тестовое покрытие:
- Тест на post: создание. Предусловия: подготовленные тестовые данные
- Тест на delete: удаление. Предусловия: созданный пользователь
- Тест на patch: изменение. Предусловия: созданный пользователь

- Get после создания, изменения
- Тест на 405 ошибку: Предусловия: ничего не нужно
- 404 422 ошибки на delete patch
- 404 на удаленного пользователя
- user flow: создаем, читаем, обновляем, удаляем
- валидность тестовых данных (емейл, урл)
- отправить модель без поля на создание


**Установка**

Клонируйте репозиторий:
```bash
git clone <URL этого репозитория>
```

Перейдите в директорию проекта:
```bash
cd <имя директории куда скачали репозиторий>
```

Установите необходимые зависимости:
```bash
pip install -r requirements.txt
```

Поднимаем postresql в контейнера(установите перед этим Docker)
```bash
docker compose up
```

Проводим миграцию, это для создания таблицы нужно
```bash
alembic upgrade head
```

**Запуск**

Чтобы запустить сервис, выполните команду:
```bash
python -m  uvicorn  app.main:app --reload --host=127.0.0.1 --port=8002
```
Проверялся запуск на windows, как на других ОС, как работает не проверял.

Eсли команда выше не сработала, то попробуйте эту
```bash
python -m  uvicorn --app-dir  ./app main:app --reload --host=127.0.0.1 --port=8002
```


**Тестирование**

Для запуска тестов используйте:
Перед тем как запустить тесты откройте новую console, чтобы там ввести эту команду
```bash
pytest .\tests\ -v
```
