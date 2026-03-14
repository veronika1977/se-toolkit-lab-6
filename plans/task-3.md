# Task 3: Системный агент - План реализации

## Обзор
Добавление инструмента `query_api` для взаимодействия с живым бэкендом.

## Конфигурация
- LLM_API_KEY, LLM_API_BASE, LLM_MODEL - из .env.agent.secret (Qwen на VM)
- LMS_API_KEY - из .env.docker.secret (для бэкенда)
- AGENT_API_BASE_URL - URL бэкенда (http://localhost:42002 или VM)

## Инструмент query_api
- method: GET, POST, etc.
- path: эндпоинт (например, "/items/")
- body: опционально JSON

## Системный промпт
Правила выбора инструментов:
- read_file/list_files: документация, код, конфиги
- query_api: данные из БД, статус коды, аналитика

## Регрессионные тесты
1. Вопрос о количестве элементов → query_api
2. Вопрос о фреймворке → read_file
## Системный промпт
Правила выбора инструментов:
- read_file/list_files: документация, код, конфиги
- query_api: данные из БД, статус коды, аналитика

## Текущие результаты benchmark
Запустил run_eval.py до изменений:
- [ ] Прошло: 0/10 тестов (агент из Task 2 не умеет работать с API)
- Первые ошибки: все вопросы, требующие query_api, падают

## План реализации

### Шаг 1: Настройка переменных окружения
- [ ] Добавить в agent.py:
  - `LMS_API_KEY = os.getenv("LMS_API_KEY")` - ключ для backend
  - `AGENT_API_BASE_URL = os.getenv("AGENT_API_BASE_URL", "http://localhost:42002")`
- [ ] Проверить загрузку из .env.docker.secret

### Шаг 2: Реализация query_api tool
- [ ] Функция:
```python
def query_api(method: str, path: str, body: str = None) -> str:
    headers = {"X-API-Key": LMS_API_KEY}
    url = f"{AGENT_API_BASE_URL}{path}"
    try:
        response = requests.request(method, url, headers=headers, json=json.loads(body) if body else None, timeout=10)
        return json.dumps({"status_code": response.status_code, "body": response.text})
    except Exception as e:
        return json.dumps({"status_code": 500, "body": str(e)})
