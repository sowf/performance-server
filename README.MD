# performance-server

### Запуск

```shell
docker-compose up
```

### Роуты

Получение всех видов загрузки (ЦПУ, ОЗУ, ГПУ)
```shell
GET /api/performance/
```

Получение определенных видов загрузки
```shell
POST /api/performance/

{
  "type": ["cpu", "gpu", "ram"]
}
```

Получение всех записей из Redis в формате JSON
```shell
GET /api/manager/
```

Получение записей из Redis, если `from` и `to` пустые - 
будут удалены все записи
```shell
POST /api/manager/

{
  "from": "MM:DD:hh:mm:ss",
  "to": "MM:DD:hh:mm:ss"
}
```