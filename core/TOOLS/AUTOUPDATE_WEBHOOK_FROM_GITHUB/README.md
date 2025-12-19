# GitHub Webhook Auto-Update System

Автоматическое обновление приложения при push в GitHub репозиторий.

## Как это работает

1. GitHub отправляет webhook на ваш сервер при каждом push
2. Webhook сервис проверяет подпись для безопасности
3. Выполняется `git pull` для получения изменений
4. Контейнеры пересобираются и перезапускаются автоматически

## Установка

### 1. Запустите production версию с webhook

```bash
# Запустить оба сервиса (приложение + webhook)
docker-compose -f docker-compose.prod.yml up -d --build

# Проверить логи
docker-compose -f docker-compose.prod.yml logs -f webhook
```

### 2. Настройте GitHub Webhook

1. Перейдите в ваш репозиторий на GitHub
2. Settings → Webhooks → Add webhook
3. Заполните форму:
   - **Payload URL**: `http://your-server-ip:9002/push_and_update_server`
   - **Content type**: `application/json`
   - **Secret**: `nakama_webhook_secret_2025_secure_key` (из .env)
   - **Events**: Just the push event
   - **Active**: ✓

4. Нажмите "Add webhook"

### 3. Проверьте работу

```bash
# Проверка здоровья webhook сервиса
curl http://localhost:9002/health

# Проверьте логи webhook
docker logs flask_cards_webhook -f

# Сделайте тестовый push в GitHub и наблюдайте за автообновлением
```

## Архитектура

```
GitHub Push Event
      ↓
Webhook (port 9002)
      ↓
Проверка подписи
      ↓
git pull
      ↓
docker-compose down
      ↓
docker-compose up -d --build
      ↓
Приложение обновлено!
```

## Безопасность

- ✅ Webhook проверяет HMAC SHA1 подпись от GitHub
- ✅ Секрет хранится в .env файле
- ✅ Только POST запросы на `/push_and_update_server`
- ✅ Блокировка одновременных обновлений

## Порты

- **5002** - Flask приложение
- **9002** - Webhook сервис

## Troubleshooting

### Webhook не срабатывает

```bash
# Проверьте логи
docker logs flask_cards_webhook

# Проверьте, что контейнер запущен
docker ps | grep webhook

# Проверьте доступность порта
curl http://localhost:9002/health
```

### Git pull fails

```bash
# Зайдите в контейнер
docker exec -it flask_cards_webhook bash

# Проверьте git статус
cd /app && git status

# Проверьте права
ls -la /app
```

### Docker permission denied

Убедитесь что webhook контейнер имеет доступ к Docker socket:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

## Отключение webhook

```bash
# Остановить только webhook
docker-compose -f docker-compose.prod.yml stop webhook

# Или использовать обычный docker-compose без webhook
docker-compose up -d
```
