# Лабораторная работа №2. Backend

REST API для системы управления студентами общежития. Вариант — **FastAPI**.
Интерфейс из Лабораторной работы №1 переведён на это API: данные больше не лежат
в cookies браузера, их хранит и проверяет сервер.

- Сервер: Python 3.11+, FastAPI, Pydantic v2, uvicorn.
- Хранение: словарь в памяти + файл `backend/data/students.json`.
- Клиент: те же три страницы на чистых HTML/CSS/JS, их раздаёт сам FastAPI.

Подробный разбор устройства проекта и ответы на вопросы к защите — в [REPORT.md](REPORT.md).

---

## Запуск

```
git clone https://github.com/fafakaj/web_lab_2.git
cd web_lab_2
```

**Windows** (из корня проекта):

```
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Linux / macOS** — то же самое, но окружение создаётся и включается иначе:

```
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

После запуска:

| Что | Адрес |
|---|---|
| Интерфейс | <http://localhost:8000/> |
| Swagger UI | <http://localhost:8000/docs> — метода **QUERY** там нет, Swagger его не показывает; проверяйте его curl'ом |

> **Запускайте без `--workers`.** Данные живут в памяти процесса: при нескольких
> воркерах у каждого была бы своя копия словаря, и они затирали бы файл друг друга.

Если после правки кода `--reload` не перезапустил сервер, остановите его `Ctrl+C`
и запустите снова.

---

## Структура

```
web_lab_2/
  README.md                 этот файл
  REPORT.md                 учебный отчёт: устройство, путь запроса, ответы к защите
  backend/
    requirements.txt
    app/
      main.py               создание приложения, lifespan, обработчики ошибок, раздача фронтенда
      routes.py             маршруты /api/requests (контроллер)
      service.py            бизнес-логика: уникальность ИСУ, даты, слияние при PATCH, фильтрация, свои исключения
      repository.py         хранение: словарь + JSON-файл + threading.Lock
      schemas.py            Pydantic-модели и структурная валидация
      errors.py             перевод ошибок в HTTP: единый формат, русские сообщения
    data/students.json      данные (8 демо-студентов)
    examples/*.json         тела запросов для проверок curl'ом
  frontend/
    index.html  student-form.html  student-info.html  image.png
    css/styles.css
    js/api.js  js/list.js  js/form.js  js/info.js
```

---

## API

Все тела запросов и ответов — JSON. Идентификатор студента — **ИСУ** (строка из 6 цифр).

| Метод | Путь | Тело запроса | Успех | Что делает |
|---|---|---|---|---|
| GET | `/api/requests` | — | 200, массив | список; фильтры в query-параметрах |
| GET | `/api/requests/{isu_id}` | — | 200, студент | один студент |
| POST | `/api/requests` | студент целиком | 201, созданный студент | создание |
| PATCH | `/api/requests/{isu_id}` | изменяемые поля | 200, обновлённый студент | частичное обновление |
| DELETE | `/api/requests/{isu_id}` | — | 204, без тела | удаление |
| QUERY | `/api/requests` | фильтры | 200, массив | тот же список, но фильтры в теле |

**Студент:**

```json
{
  "isu_id": "412345",
  "full_name": "Иванов Иван Иванович",
  "group": "M3301",
  "dormitory": "alp",
  "room": "1205",
  "check_in": "2024-09-01",
  "check_out": null,
  "is_foreign": false,
  "notes": ""
}
```

`dormitory` — код общежития: `sg`, `alp`, `bel`, `len`, `msg`. `check_out: null` — студент ещё проживает.

**Фильтры** (все необязательные; в GET — query-параметры, в QUERY — поля JSON-тела):
`full_name` (подстрока без учёта регистра), `group`, `dormitory`, `room`,
`is_foreign` (`true`/`false`), `living` (`true` — `check_out` пустой, `false` — заполнен).

Интерфейс сам выбирает метод: до трёх непустых фильтров — `GET ?…`, четыре и больше — `QUERY`.

**Ошибки** всегда приходят в одном формате:

```json
{
  "error": {
    "status": 422,
    "code": "VALIDATION_ERROR",
    "message": "Данные не прошли проверку",
    "details": [
      {"field": "room", "message": "Комната — ровно 4 цифры, первая не 0, например 1205"}
    ]
  }
}
```

| Код | `code` | Когда |
|---|---|---|
| 400 | `BAD_REQUEST` | битый JSON, тело не объект, тела нет, нет `Content-Type: application/json`, пустой PATCH |
| 404 | `NOT_FOUND` | нет студента с таким ИСУ; неизвестный адрес |
| 405 | `METHOD_NOT_ALLOWED` | метод не поддерживается для адреса |
| 409 | `CONFLICT` | студент с таким ИСУ уже есть |
| 422 | `VALIDATION_ERROR` | поля не прошли проверку (формат или правила дат) |
| 500 | `INTERNAL_ERROR` | непредвиденная ошибка на сервере |

---

## Проверка curl'ом

Команды выполняются из папки `backend/` при запущенном сервере. Тела запросов лежат
в `examples/` и передаются как `-d "@examples/файл.json"`, поэтому одинаково
работают в bash и в PowerShell.

- В **PowerShell** пишите `curl.exe`, а не `curl`: в Windows PowerShell `curl` — это
  псевдоним другой команды (`Invoke-WebRequest`).
- Кавычки вокруг адресов с `&` и вокруг `@examples/…` обязательны в обеих оболочках.
- Кириллицу прямо в командной строке (`-d '{"full_name": "Иванов"}'`) в Windows
  передавать не стоит: она дойдёт до сервера не в UTF-8, и он ответит 400. Для этого
  и нужны файлы.
- Добавьте `-i`, чтобы увидеть статус и заголовки ответа.

| № | Проверка | Команда | Ожидается |
|---|---|---|---|
| 1 | Список | `curl "http://localhost:8000/api/requests"` | 200 |
| 1 | Фильтр через query | `curl "http://localhost:8000/api/requests?group=M3301&dormitory=alp"` | 200, 3 студента |
| 2 | QUERY с 4 фильтрами | `curl -X QUERY "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/query.json"` | 200, 2 студента |
| 2 | QUERY без фильтров | `curl -X QUERY "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/empty.json"` | 200, все |
| 3 | Студент по ИСУ | `curl "http://localhost:8000/api/requests/412345"` | 200 |
| 3 | Нет такого ИСУ | `curl "http://localhost:8000/api/requests/999999"` | 404 |
| 3 | ИСУ не из цифр | `curl "http://localhost:8000/api/requests/abc"` | 422 |
| 4 | Создание | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create.json"` | 201 |
| 4 | Тот же ИСУ ещё раз | та же команда | 409 |
| 5 | Битый JSON | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/broken.json"` | 400 |
| 5 | Тело `[1]` | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/array.json"` | 400 |
| 5 | Без тела | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json"` | 400 |
| 6 | Группа кириллицей | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_group.json"` | 422 |
| 6 | Комната `0123` | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_room_zero.json"` | 422 |
| 6 | Комната `512` | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_room_short.json"` | 422 |
| 6 | ФИО из одного слова | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_name.json"` | 422 |
| 6 | `is_foreign: "yes"` | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_foreign.json"` | 422 |
| 6 | `check_in: 946684800` | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_check_in.json"` | 422 |
| 6 | Выселение раньше заселения | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_check_out_before.json"` | 422 |
| 6 | Выселение позже 9 лет | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_check_out_late.json"` | 422 |
| 6 | Лишнее поле | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_extra.json"` | 422 |
| 6 | ИСУ числом | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_isu.json"` | 422 |
| 7 | PATCH одним полем | `curl -X PATCH "http://localhost:8000/api/requests/415001" -H "Content-Type: application/json" -d "@examples/patch_one.json"` | 200 |
| 7 | PATCH пустой | `curl -X PATCH "http://localhost:8000/api/requests/415001" -H "Content-Type: application/json" -d "@examples/empty.json"` | 400 |
| 7 | PATCH с `isu_id` | `curl -X PATCH "http://localhost:8000/api/requests/415001" -H "Content-Type: application/json" -d "@examples/patch_isu.json"` | 422 |
| 7 | PATCH дата выселения | `curl -X PATCH "http://localhost:8000/api/requests/415001" -H "Content-Type: application/json" -d "@examples/patch_check_out.json"` | 200 |
| 7 | PATCH `check_out: null` | `curl -X PATCH "http://localhost:8000/api/requests/415001" -H "Content-Type: application/json" -d "@examples/patch_living.json"` | 200 |
| 7 | PATCH чужого ИСУ | `curl -X PATCH "http://localhost:8000/api/requests/999999" -H "Content-Type: application/json" -d "@examples/patch_one.json"` | 404 |
| 8 | Удаление | `curl -i -X DELETE "http://localhost:8000/api/requests/415001"` | 204, тела нет |
| 8 | Удаление повторно | та же команда | 404 |
| 9 | Неизвестный параметр | `curl "http://localhost:8000/api/requests?foo=1"` | 422 |
| 9 | Пустой параметр | `curl "http://localhost:8000/api/requests?group="` | 422 |
| 9 | QUERY: ФИО из одной буквы | `curl -X QUERY "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/query_bad_name.json"` | 422 |
| 10 | Неверный метод | `curl -X PUT "http://localhost:8000/api/requests"` | 405 |
| 10 | Неизвестный адрес | `curl "http://localhost:8000/api/nope"` | 404 |
| 11 | Внутренняя ошибка | см. ниже | 500 |
| 12 | Данные после перезапуска | см. ниже | 200 |

### 11. Как перехватывается 500

В [backend/app/errors.py](backend/app/errors.py) есть обработчик `unexpected_error_handler`,
а [backend/app/main.py](backend/app/main.py) регистрирует его на базовый класс `Exception`:

```python
app.add_exception_handler(Exception, unexpected_error_handler)
```

Любое исключение, которое никто не поймал (ошибка в коде, деление на ноль, сбой диска),
доходит до самого внешнего слоя Starlette — `ServerErrorMiddleware`. Он вызывает наш
обработчик, и клиент получает 500 в едином формате с общим текстом, без трассировки:
подробности ошибки наружу не отдаются. После этого middleware заново бросает
исключение, и uvicorn печатает полную трассировку в консоль сервера.

Как проверить:

1. В `backend/app/routes.py` в функции `get_student` первой строкой добавить `1 / 0`.
2. Перезапустить сервер.
3. `curl -i "http://localhost:8000/api/requests/412345"` → `500`, тело
   `{"error": {"status": 500, "code": "INTERNAL_ERROR", "message": "Внутренняя ошибка сервера. Подробности записаны в консоль сервера", "details": []}}`,
   в консоли — `ZeroDivisionError: division by zero` с трассировкой.
4. **Убрать `1 / 0` обратно.**

### 12. Данные сохраняются в файл

1. Создать студента (`examples/create.json`) → 201.
2. Остановить сервер (`Ctrl+C`) и запустить снова.
3. `curl "http://localhost:8000/api/requests/415001"` → 200: запись прочитана из
   `backend/data/students.json`.
4. Удалить её (`DELETE`), чтобы вернуть демо-данные.

Если файла нет, при старте он создаётся с пустым списком `[]`. Если JSON в файле
повреждён, сервер **не запускается** и пишет, какой файл и где сломан: данные
молча не затираются.
