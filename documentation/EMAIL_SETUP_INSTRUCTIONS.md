# Инструкция по настройке email для отправки писем

## Настройка SMTP сервера

### 1. Выберите провайдера email

#### Gmail (рекомендуется)
1. Включите двухфакторную аутентификацию в Google аккаунте
2. Создайте пароль приложения:
   - Перейдите в настройки Google аккаунта
   - Безопасность → Пароли приложений
   - Создайте новый пароль для приложения
3. Используйте настройки:
   ```
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   ```

#### Yandex Mail
1. Включите SMTP в настройках Yandex
2. Используйте настройки:
   ```
   EMAIL_HOST=smtp.yandex.ru
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   ```

#### Mail.ru
1. Включите SMTP в настройках Mail.ru
2. Используйте настройки:
   ```
   EMAIL_HOST=smtp.mail.ru
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   ```

### 2. Настройте файл email_config.env

Отредактируйте файл `email_config.env` в корне проекта:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 3. Перезапустите сервер

После изменения настроек перезапустите Django сервер:

```bash
python manage.py runserver
```

### 4. Тестирование

Для тестирования отправки email используйте:

```bash
curl -X POST http://127.0.0.1:8000/ru/auth/send-email-code/ \
  -H "Content-Type: application/json" \
  -d '{
    "email":"test@example.com",
    "first_name":"Тест",
    "last_name":"Тестов",
    "phone":"+79991234567",
    "password":"password123",
    "password_confirm":"password123"
  }'
```

### 5. Безопасность

- Никогда не коммитьте файл `email_config.env` в git
- Используйте пароли приложений вместо обычных паролей
- Для продакшена используйте переменные окружения сервера

### 6. Отладка

Если письма не отправляются, проверьте:

1. Правильность настроек SMTP
2. Доступность интернета
3. Блокировку файрволом
4. Логи Django сервера

Для отладки временно включите консольный вывод:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```








