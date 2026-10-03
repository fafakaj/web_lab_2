# Лабораторная работа №2. Учебный отчёт

Этот документ — не отчёт для сдачи, а разбор проекта для подготовки к защите. В коде
нет ни одного комментария (так было и в Лабе 1), поэтому все «почему сделано так»
собраны здесь. Ссылки на лекции даны по названиям слайдов: например, «лекция 5,
слайд „Путь запроса в FastAPI“».

Как читать:

- разделы 1–2 — что лежит в проекте и зачем нужна каждая строка;
- раздел 3 — что происходит от нажатия кнопки до записи в файл;
- разделы 4–7 — справочник по API, валидации, кодам ответа и отличиям от Лабы 1;
- раздел 8 — ответы на 18 вопросов к защите;
- раздел 9 — сценарий показа работы на 3–5 минут.

## Содержание

1. [Ход работы](#1-ход-работы)
2. [Как устроен проект](#2-как-устроен-проект)
3. [Путь запроса от кнопки до файла и обратно](#3-путь-запроса-от-кнопки-до-файла-и-обратно)
4. [API](#4-api)
5. [Валидация](#5-валидация)
6. [Коды ответов и формат ошибок](#6-коды-ответов-и-формат-ошибок)
7. [Что изменилось по сравнению с Лабой 1 и почему](#7-что-изменилось-по-сравнению-с-лабой-1-и-почему)
8. [Ответы на вопросы к защите](#8-ответы-на-вопросы-к-защите)
9. [Как показать работу на защите](#9-как-показать-работу-на-защите)

---

## 1. Ход работы

Шаги перечислены в том порядке, в котором проект писался.

1. **Разбор задания.** Прочитаны `Лаб 2.pdf`, лекции 1–5 и Лаба 1. Из задания выписаны:
   6 обязательных запросов, фильтрация через query-параметры и метод QUERY, 5 обязательных
   требований, единый формат ошибок, 8 кодов ответа. Модель студента взята из Лабы 1. Ключи
   стали полными (`fio` → `full_name`), отдельного числового `id` больше нет: идентификатор —
   ИСУ (требование 3).
2. **Окружение.** Создано виртуальное окружение `venv`, установлены `fastapi` и `uvicorn[standard]`.
   Проект проверялся на FastAPI 0.142.2, Starlette 1.7.0, Pydantic 2.13.5, uvicorn 0.54.0,
   Python 3.14. Эти версии записаны в `requirements.txt`.
3. **`schemas.py` — модели данных (DTO).** Описаны входные модели `StudentCreate` и
   `StudentUpdate`, выходная `StudentOut` и фильтр `StudentFilter`. Здесь же вся структурная
   проверка: шаблоны, длины, допустимые значения, запрет лишних полей.
4. **`repository.py` и `data/students.json` — хранение.** Словарь в памяти, загрузка файла
   при старте и запись файла целиком после каждого изменения под `threading.Lock`. Подготовлены
   8 демо-студентов: все 5 общежитий, 3 иностранца, проживающие и выселенные, трое из `M3301`
   в общежитии `alp`.
5. **`service.py` — бизнес-логика.** Свои исключения сервиса, уникальность ИСУ, правила дат,
   слияние при PATCH, фильтрация генераторным выражением.
6. **`errors.py` — перевод ошибок в HTTP.** Функция единого формата ответа и четыре
   обработчика (ошибки сервиса, ошибки Pydantic, HTTP-ошибки, всё остальное). Русские
   подсказки по полям.
7. **`routes.py` — контроллер.** Шесть маршрутов без логики. Сервис подключается через
   `Depends(get_service)`.
8. **`main.py` — сборка приложения.** `lifespan` создаёт репозиторий, регистрируются
   обработчики ошибок, подключается роутер, на `/` монтируется фронтенд.
9. **Проверка curl'ом.** 43 запроса: 35 команд из `README.md` и ещё 8 крайних случаев
   (тело без `Content-Type`, `PATCH` с датой выселения раньше заселения, явный `null`
   в `full_name` и другие). Все коды совпали с ожидаемыми. Отдельно проверено:
   - 500 через временное `1 / 0`;
   - перезапуск сервера: данные на месте;
   - отсутствующий и повреждённый файл данных;
   - гонка: 20 одновременных POST с одним ИСУ дали ровно один ответ 201 и 19 ответов 409,
     а 40 одновременных POST с разными ИСУ все попали в файл.

   По ходу выяснились две вещи, которые повлияли на код:
   - FastAPI 0.142 отмечает битый JSON адресом `("body", позиция)`, а не `("body",)`;
   - в Pydantic `\d` пропускает «нелатинские» цифры (см. раздел 5).
10. **Фронтенд, `api.js`.** Фронтенд Лабы 1 скопирован. `storage.js` стал `api.js`: cookies
    и миграция удалены, добавлены функции на `fetch` и класс `ApiError`, выбор между GET и QUERY.
11. **`index.html` и `list.js`.** Над таблицей появилась форма фильтров, состояние фильтров
    хранится в адресе страницы, удаление идёт через API.
12. **`student-form.html` и `form.js`.** Поля переименованы, HTML-атрибуты ужесточены,
    `min`/`max` у дат выставляются из JS. `validate()` и `isIsuTaken()` удалены: эти
    проверки теперь на сервере. Ошибки сервера выводятся под полями.
13. **`info.js`.** Досье берёт данные через `getStudent`.
14. **Проверка в браузере.** Сценарии прогнаны в Chromium через Playwright (34 проверки):
    - список, фильтр GET, фильтр QUERY, пустой результат;
    - ошибка в строке статуса;
    - добавление, 409 и 422 под полями;
    - редактирование, досье, удаление;
    - обрыв сети;
    - отсутствие cookies и `localStorage`;
    - вёрстка на ширине 375 px.
15. **Документы.** `README.md` (запуск и проверки) и этот отчёт.
16. **Архитектурный обзор и две правки.**
    - **Гонка в PATCH.** `service.update` сначала читал запись (один захват замка), а потом
      записывал (второй захват). Если два PATCH к одному студенту шли одновременно, оба
      могли прочитать старую версию, и одно изменение терялось. При обычной работе GIL это
      почти не проявлялось: 0 потерь из 2000. Когда интерпретатор заставили переключать
      потоки чаще (`sys.setswitchinterval(1e-6)`), потерялось 1457 изменений из 2000.
      Исправление: `repository.update` принимает функцию изменения и выполняет
      «прочитать — слить — проверить — записать» под одним замком. После исправления в том
      же режиме 0 из 2000.
    - **Исключения сервиса перенесены из `errors.py` в `service.py`.** До этого
      `import app.service` через `errors.py` подтягивал FastAPI.

    После обеих правок заново прогнаны все проверки: curl, команды README, браузер,
    перезапуск, гонки.

---

## 2. Как устроен проект

### 2.1. Файлы и их роли

```
web_lab_2/
  README.md                 запуск, таблица API, все curl-проверки
  REPORT.md                 этот отчёт
  backend/
    requirements.txt        зависимости с точными версиями
    app/                    пакет Python с приложением
      __init__.py           пустой файл: делает папку app пакетом
      main.py               сборка: FastAPI(), lifespan, обработчики ошибок, роутер, фронтенд
      routes.py             Controller: маршруты /api/requests
      service.py            Service: бизнес-правила, фильтрация, исключения сервиса
      repository.py         Repository: словарь + JSON-файл + Lock
      schemas.py            DTO: Pydantic-модели, структурная проверка
      errors.py             перевод ошибок в HTTP: единый формат, обработчики, подсказки
    data/students.json      «база данных» — JSON-массив студентов
    examples/*.json         готовые тела запросов для curl
  frontend/                 клиент из Лабы 1, переведённый на API
    index.html              список + форма фильтров
    student-form.html       добавление / редактирование
    student-info.html       досье
    image.png               favicon с котиком
    css/styles.css          стили (палитра в :root)
    js/api.js               всё общение с сервером + общие функции отображения
    js/list.js              таблица, фильтры, удаление
    js/form.js              форма
    js/info.js              досье
```

### 2.2. Слои и направление зависимостей

Лекция 4, слайды «Controller / Service / Repository» и «Направление зависимостей»:
каждый слой знает только о слое под собой.

```
          HTTP-запрос
               │
     ┌─────────▼──────────┐   schemas.py: проверяет вход, описывает выход (DTO)
     │ routes.py          │   Controller: принять запрос, вызвать сервис, вернуть ответ
     └─────────┬──────────┘
               │ Depends(get_service)
     ┌─────────▼──────────┐   errors.py (сбоку): переводит исключения сервиса в HTTP
     │ service.py         │   Service: правила (ИСУ уникален, даты, PATCH, фильтры)
     └─────────┬──────────┘   и свои исключения (NotFoundError, ConflictError, …)
               │
     ┌─────────▼──────────┐
     │ repository.py      │   Repository: где и как лежат данные
     └─────────┬──────────┘
               │ with lock
        data/students.json
```

Кто что импортирует (это и есть «направление зависимостей»):

| Файл | Импортирует из проекта | Знает про HTTP / FastAPI? |
|---|---|---|
| `repository.py` | ничего | нет |
| `schemas.py` | ничего | нет (только Pydantic) |
| `service.py` | `repository`, `schemas` | нет: не возвращает кодов, не видит `Request` |
| `routes.py` | `schemas`, `service` | да |
| `errors.py` | `service` (классы исключений) | да (здесь исключения превращаются в HTTP-ответы) |
| `main.py` | `errors`, `repository`, `routes`, `service` | да |

`routes.py` не импортирует `repository.py`: контроллер не ходит к данным в обход сервиса
(слайд «Чего не должен делать Controller»). Сервис не знает, что его вызвали по HTTP
(слайд «Service не зависит от интерфейса»): тот же `StudentService` можно было бы вызвать
из консольной утилиты или телеграм-бота. Это проверяемо буквально: после
`import app.service` в памяти нет ни `fastapi`, ни `starlette`.

Исключения сервиса объявлены в `service.py`, а не в `errors.py`. Так стрелка идёт от
`errors.py` к сервису, а не наоборот. Лекция 4, слайд «Ошибки как часть архитектуры»: у
каждого слоя свои ошибки, бизнес-ошибки (`RoomIsFull`) нарисованы у сервиса.

### 2.3. `schemas.py` — модели данных и структурная проверка

**DTO** (Data Transfer Object, лекция 4, слайды «DTO — Data Transfer Object» и «Request DTO
и Response DTO») — объект, который описывает форму данных на границе приложения. В FastAPI
DTO — это Pydantic-модели. FastAPI сам превращает JSON из запроса в модель и проверяет его.
Если проверка не прошла, обработчик даже не вызывается.

Сначала в файле объявлены переиспользуемые типы. Каждый тип — это базовый тип плюс проверки:

```python
DormitoryCode = Literal["sg", "alp", "bel", "len", "msg"]

NAME_WORD = r"[A-Za-zА-ЯЁа-яё]+(?:['\-][A-Za-zА-ЯЁа-яё]+)*"
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
```

- `Literal[...]` — «одно из перечисленных значений». Код общежития вне списка даёт 422.
- `NAME_WORD` — одно слово ФИО: буквы, и внутри слова можно дефис или апостроф
  (`Римский-Корсаков`, `О'Брайен`). `(?:...)` — группа без запоминания, `*` — «сколько угодно раз».
- `ISO_DATE` — заранее скомпилированное регулярное выражение для даты `ГГГГ-ММ-ДД`.

Четыре маленькие функции готовят значение **до** проверки шаблоном:

```python
def collapse_spaces(value):
    if isinstance(value, str):
        return " ".join(value.split())
    return value
```

`value.split()` без аргументов режет строку по любым пробельным символам и выбрасывает
пустые куски, а `" ".join(...)` склеивает обратно через один пробел. Так
`"  Соколова   Елена "` превращается в `"Соколова Елена"`. Проверка `isinstance` нужна,
чтобы не упасть на числе или `null`: такое значение пропускается дальше, и Pydantic сам
скажет, что ждал строку. `strip_upper` делает `strip()` + `upper()` для группы (`m3302` →
`M3302`), `strip` обрезает пробелы по краям заметок.

```python
def require_iso_date(value):
    if isinstance(value, str) and ISO_DATE.fullmatch(value):
        return value
    raise ValueError("date must be a YYYY-MM-DD string")
```

По умолчанию Pydantic щедр: он примет как дату и число `946684800` (секунды с 1970 года), и
строку со временем `"2024-09-01T00:00:00"`. Мы хотим только ровно `ГГГГ-ММ-ДД`, поэтому
пропускаем дальше только такую строку. `fullmatch` требует, чтобы шаблону соответствовала
вся строка, а не её часть. Брошенный `ValueError` Pydantic превратит в ошибку валидации
(в итоге 422).

Из этих кусков собраны типы полей:

```python
IsuId = Annotated[str, Field(pattern=r"^[0-9]{6}$")]
FullName = Annotated[
    str,
    BeforeValidator(collapse_spaces),
    Field(min_length=5, max_length=100, pattern=rf"^{NAME_WORD}(?: {NAME_WORD})+$"),
]
Group = Annotated[str, BeforeValidator(strip_upper), Field(pattern=r"^[A-Z][0-9]{4}$")]
Room = Annotated[str, Field(pattern=r"^[1-9][0-9]{3}$")]
IsoDate = Annotated[date, BeforeValidator(require_iso_date)]
Notes = Annotated[str, BeforeValidator(strip), Field(max_length=500)]
```

- `Annotated[тип, доп. сведения]` — стандартный способ Python приклеить к типу метаданные.
  Сам Python их не использует, а Pydantic читает: `Field(...)` задаёт ограничения,
  `BeforeValidator(f)` — функцию, которая выполнится **до** основной проверки.
- `BeforeValidator(collapse_spaces)` — то же самое, что `@field_validator("full_name", mode="before")`
  в виде декоратора над методом модели. Только тип можно один раз описать и
  переиспользовать в трёх моделях. Порядок важен: сначала нормализация, потом шаблон.
  Иначе `"Иванов  Иван"` с двумя пробелами не прошёл бы шаблон с одним пробелом.
- Шаблон ФИО: `^слово(?: слово)+$` — минимум два слова через ровно один пробел (лишние
  пробелы к этому моменту уже схлопнуты).
- `Room`: `[1-9][0-9]{3}` — ровно 4 цифры, первая не ноль.
- Везде `[0-9]`, а не `\d`. В Python и в движке регулярных выражений Pydantic `\d` означает
  **любую** десятичную цифру Unicode, например арабские `١٢٣٤٥٦`. Это проверено:
  `Field(pattern=r"^\d{6}$")` такую строку принимает, `[0-9]` — нет.

Сами модели:

```python
class StudentCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    isu_id: IsuId
    full_name: FullName
    group: Group
    dormitory: DormitoryCode
    room: Room
    check_in: IsoDate
    check_out: IsoDate | None = None
    is_foreign: StrictBool
    notes: Notes = ""
```

- `model_config = ConfigDict(extra="forbid")` — неизвестное поле (`"age": 20`) даёт ошибку
  `extra_forbidden`, а не молча выбрасывается. Опечатка клиента в имени поля сразу видна.
- Поле без значения по умолчанию обязательное. `check_out` и `notes` имеют значения по
  умолчанию, поэтому их можно не присылать.
- `IsoDate | None` — «дата или `null`». `null` означает «ещё проживает».
- `StrictBool` принимает только `true`/`false`. Обычный `bool` в Pydantic принял бы и `"yes"`,
  и `1`, и `"true"`.
- `isu_id: str`: строка, а не число. ИСУ — идентификатор, а не величина: его не складывают,
  и у него могут быть ведущие нули. Pydantic v2 не превращает число в строку сам, поэтому
  `"isu_id": 415002` даёт 422.

```python
class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: FullName = None
    group: Group = None
    ...
    check_out: IsoDate | None = None
    is_foreign: StrictBool = None
    notes: Notes = None
```

Модель для PATCH. В ней **нет** `isu_id`, поэтому попытка его поменять даёт 422
«Неизвестное поле». Все поля необязательны: у каждого значение по умолчанию `None`.
Хитрость `full_name: FullName = None`: Pydantic не проверяет значение по умолчанию, поэтому
непереданное поле просто остаётся `None`. А вот **явный** `"full_name": null` проверяется
как строка и даёт 422. Явный `null` разрешён только у `check_out`, потому что там тип
`IsoDate | None`.

```python
class StudentOut(BaseModel):
    isu_id: str
    ...
    check_in: date
    check_out: date | None
    is_foreign: bool
    notes: str
```

Response DTO — что сервер обещает вернуть. Проверки ему не нужны: данные уже проверены на
входе. Его задача — гарантировать набор полей и превратить `date` обратно в строку ISO при
сериализации.

```python
class StudentFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: NamePart | None = None
    group: Group | None = None
    dormitory: DormitoryCode | None = None
    room: Room | None = None
    is_foreign: bool | None = None
    living: bool | None = None
```

Одна модель фильтров для GET (поля из query-параметров) и для QUERY (поля из JSON-тела).
`NamePart` мягче `FullName`: можно часть фамилии от 2 символов. `is_foreign` и `living`
здесь обычный `bool`, а не `StrictBool`: в адресе страницы всё — строки, и `?living=true`
должен превратиться в `True`.

### 2.4. `repository.py` — хранение

Лекция 4, слайды «Repository как абстракция» и «Зачем нужен Repository»: сервис не знает,
где лежат данные (файл, PostgreSQL, память), он вызывает `get`, `add`, `delete`.

```python
DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "students.json"
```

`__file__` — путь к самому `repository.py`. От него поднимаемся на два уровня (`app/` →
`backend/`) и спускаемся в `data/`. Путь не зависит от того, из какой папки запустили
сервер. Путь от текущей папки (`"data/students.json"`) сломался бы при запуске из корня
проекта.

```python
class StudentRepository:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.students: dict[str, dict] = {}
        self.lock = threading.Lock()
```

- `self.students` — словарь «ИСУ → запись». Поиск по ключу мгновенный, а с Python 3.7 словарь
  помнит порядок вставки, поэтому список отдаётся в порядке добавления без сортировки.
- `self.lock` — один замок на весь репозиторий (лекция 5, слайд «Гонка при записи в JSON-файл»:
  `with lock: # one per repository`).

```python
    def load(self) -> None:
        if not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("[]", encoding="utf-8")

        try:
            records = json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise RuntimeError(
                f"Файл {self.path} повреждён ({error}). Сервер не запущен, данные не тронуты: "
                f"исправьте JSON вручную или удалите файл, чтобы начать с пустого списка."
            ) from error

        if not isinstance(records, list):
            raise RuntimeError(f"В файле {self.path} должен лежать JSON-массив студентов.")

        self.students = {record["isu_id"]: record for record in records}
```

- Если файла нет, создаём его с пустым массивом.
- Если JSON битый, **не** начинаем с пустого списка: первая же запись затёрла бы файл, и
  данные пропали бы без следа. Вместо этого бросаем `RuntimeError`, `lifespan` падает, uvicorn
  пишет «Application startup failed» и выходит. `raise ... from error` сохраняет исходную
  ошибку в трассировке, видно номер строки и столбца.
- Последняя строка — генератор словаря (dict comprehension): из списка записей строим словарь
  по ключу `isu_id`.

```python
    def save(self) -> None:
        records = list(self.students.values())
        self.path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
```

Файл переписывается **целиком**. `ensure_ascii=False` пишет кириллицу как есть, а не
`Ив...`; `indent=2` — с отступами, чтобы файл можно было читать глазами.
`save` сам замок **не берёт**: его вызывают только методы, которые замок уже держат.
Это совет со слайда «RLock: лок, который можно взять повторно»: «Часто лучше без RLock:
вынести запись в функцию, которая лок не берёт и вызывается только под ним». Если бы `save`
делал `with self.lock`, а его вызывал `add`, который тоже под `with self.lock`, поток ждал бы
сам себя вечно (слайд «Deadlock», самоблокировка).

```python
    def list_all(self) -> list[dict]:
        with self.lock:
            return list(self.students.values())

    def add(self, student: dict) -> bool:
        with self.lock:
            if student["isu_id"] in self.students:
                return False
            self.students[student["isu_id"]] = student
            self.save()
            return True
```

- Даже чтение идёт под замком. Если перебирать словарь циклом, пока другой поток добавляет
  ключ, Python бросит `RuntimeError: dictionary changed size during iteration`. В обычном
  CPython `list(...)` проходит словарь за один шаг под GIL, но это деталь реализации: в
  сборке Python без GIL её нет. Замок делает гарантию явной: снимок списка снимается, пока
  никто не пишет.
- `add` проверяет «ИСУ занят?» и вставляет запись **внутри одного** `with`. Если бы сервис
  сначала спросил `exists()`, а потом вызвал `add()`, два одновременных POST с одним ИСУ оба
  увидели бы «свободно» и оба записались бы. Это ровно гонка со слайда «Гонка при записи в
  JSON-файл»: «Lock делает „прочитать — изменить — записать“ одним шагом». Проверено:
  20 одновременных POST с одинаковым ИСУ → один 201 и девятнадцать 409. Так же устроен
  первичный ключ в базе данных: уникальность гарантирует хранилище, а что это значит для
  пользователя (409 и текст), решает сервис.
- Метод возвращает `True`/`False`, а не бросает HTTP-ошибку: репозиторий ничего не знает о
  кодах ответа.

```python
    def update(self, isu_id: str, change: Callable[[dict], dict]) -> dict | None:
        with self.lock:
            current = self.students.get(isu_id)
            if current is None:
                return None
            student = change(current)
            self.students[isu_id] = student
            self.save()
            return student
```

`update` устроен хитрее, потому что PATCH — это «прочитать — слить — проверить — записать».
Если бы сервис сначала прочитал запись (`get`, замок взят и отпущен), а потом записал
(`update`, замок взят снова), то между этими шагами другой поток успел бы сделать то же
самое:

```
поток A: прочитал v1          поток B: прочитал v1
поток A: записал v1 + room    поток B: записал v1 + notes   ← изменение room потеряно
```

Это та же гонка со слайда «Гонка при записи в JSON-файл»: «два потока прочитали одно
значение — одно обновление потеряно». Поэтому `update` принимает не готовую запись, а
**функцию** `change`: «вот как из текущей записи получить новую». Репозиторий вызывает её
внутри своего `with self.lock`, и чтение, слияние, проверка и запись становятся одним шагом.

- `Callable[[dict], dict]` — аннотация «функция, которая принимает словарь и возвращает словарь».
- Если `change` бросит исключение (например, даты не прошли проверку), оно вылетит из `with`:
  замок освободится сам, а в словарь и в файл **ничего не запишется**.
- Студента нет → `None`. Получилось → новая запись, её сервис и вернёт клиенту.
- `change` не должна сама обращаться к репозиторию. `Lock` не повторный, и поток ждал бы
  сам себя (слайд «Deadlock», самоблокировка). Наша функция только сливает словари и
  проверяет даты.

Проверено: два потока одновременно шлют PATCH разных полей одному студенту, 2000 попыток,
интерпретатор переключает потоки как можно чаще. До исправления потерялось 1457 изменений,
после — 0.

`delete` устроен как `add`: «нет такого ключа» → `False`, иначе изменить словарь и
переписать файл. Записи в словаре не изменяются на месте, а **заменяются** новыми
словарями, поэтому тот, кто уже получил старую запись, видит её целиком старой, а не
наполовину изменённой.

### 2.5. `errors.py` — перевод ошибок в HTTP и единый формат

Лекция 4, слайд «Ошибки как часть архитектуры»: у каждого слоя свои ошибки, и где-то
наверху они превращаются в понятный ответ клиенту. Свои исключения объявляет сервис
(раздел 2.6), а `errors.py` их импортирует и решает, каким HTTP-ответом они станут.

```python
from app.service import ConflictError, EmptyUpdateError, NotFoundError, RuleViolationError, ServiceError

SERVICE_ERRORS = {
    NotFoundError: (404, "NOT_FOUND"),
    ConflictError: (409, "CONFLICT"),
    EmptyUpdateError: (400, "BAD_REQUEST"),
    RuleViolationError: (422, "VALIDATION_ERROR"),
}
```

Единственное место, где «бизнес-ошибка» сопоставлена HTTP-коду. Сервис бросает
`NotFoundError`, а то, что это 404, знает только `errors.py`.

```python
def error_response(status: int, code: str, message: str, details: list | None = None, headers=None) -> JSONResponse:
    content = {"error": {"status": status, "code": code, "message": message, "details": details or []}}
    return JSONResponse(status_code=status, content=content, headers=headers)
```

Единый формат собирается в одной функции, поэтому разойтись ему негде.
`details or []` — если деталей нет, будет пустой массив, а не `null`.

Обработчиков четыре, у каждого своя зона:

| Обработчик | Ловит | Ответ |
|---|---|---|
| `service_error_handler` | `ServiceError` и наследников из сервиса | 400 / 404 / 409 / 422 по таблице выше |
| `validation_error_handler` | `RequestValidationError` — данные не прошли Pydantic | 400 (тело не разобрать) или 422 (поля) |
| `http_error_handler` | `StarletteHTTPException` — ошибки самого фреймворка | 404 (нет адреса), 405 (не тот метод), 400 |
| `unexpected_error_handler` | `Exception` — всё остальное | 500 без подробностей |

Разберём самый сложный, `validation_error_handler`:

```python
def is_body_error(error: dict) -> bool:
    if error["type"] == "json_invalid":
        return True
    return tuple(error["loc"]) == ("body",) and error["type"] in BODY_ERRORS
```

Каждая ошибка Pydantic — словарь с полями `type` (что не так), `loc` (где: например,
`("body", "room")` или `("query", "group")`) и `msg`. Если `loc` равен просто `("body",)`,
значит, проблема со всем телом, а не с полем: тела нет (`missing`), это не объект
(`model_attributes_type`, `dict_type`). Битый JSON FastAPI 0.142 помечает как
`("body", позиция_ошибки)`, поэтому `json_invalid` проверяется отдельно, без сравнения `loc`.

```python
def describe(error: dict, hints: dict) -> dict:
    field = str(error["loc"][-1])

    if error["type"] == "missing":
        message = "Обязательное поле"
    elif error["type"] == "extra_forbidden":
        message = "Неизвестное поле"
    else:
        message = hints.get(field, "Некорректное значение")

    return {"field": field, "message": message}
```

Имя поля — последний элемент `loc`. Английское сообщение Pydantic (`"String should match
pattern '^[1-9][0-9]{3}$'"`) клиенту не отдаётся: вместо него берётся подсказка из словаря
`FIELD_HINTS` («Комната — ровно 4 цифры, первая не 0, например 1205»).

```python
def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()

    for error in errors:
        if is_body_error(error):
            return error_response(400, "BAD_REQUEST", BODY_ERRORS[error["type"]])

    hints = FILTER_HINTS if request.method in ("GET", "QUERY") else FIELD_HINTS
    details = [describe(error, hints) for error in errors]
    return error_response(422, "VALIDATION_ERROR", "Данные не прошли проверку", details)
```

Если тело вообще не разобрать, это 400: исправлять поля бессмысленно. Иначе 422 со
списком всех ошибок сразу, по одной на поле. Для GET и QUERY берутся подсказки фильтров:
в фильтре ФИО может быть одним словом, в форме нет.

```python
def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code, message = HTTP_ERRORS.get(exc.status_code, ("HTTP_ERROR", "Ошибка запроса"))
    return error_response(exc.status_code, code, message, headers=exc.headers)
```

Ошибки, которые рождает сам фреймворк: неизвестный адрес → 404, не тот метод → 405,
тело в неверной кодировке → 400. `headers=exc.headers` сохраняет заголовки исключения
(например, `Allow` у 405, если фреймворк его передал).

```python
def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_response(500, "INTERNAL_ERROR", "Внутренняя ошибка сервера. Подробности записаны в консоль сервера")
```

Клиенту — общий текст: трассировка могла бы раскрыть пути к файлам и куски кода.
Трассировку печатает сам Starlette. Его `ServerErrorMiddleware` после нашего ответа
пробрасывает исключение дальше («We always continue to raise the exception. This allows
servers to log the error»), и uvicorn пишет `ERROR: Exception in ASGI application` с полным
стеком.

Все обработчики — обычные `def`. Starlette умеет и такие: запускает их в пуле потоков.

### 2.6. `service.py` — бизнес-логика

Лекция 4, слайды «Business Logic» и «Validation: два типа проверки». Здесь живут правила,
которые нельзя проверить, глядя на одно поле:
- ИСУ не должен быть занят — нужно знать, что уже лежит в хранилище;
- даты зависят от «сегодня» и друг от друга;
- при PATCH даты проверяются после слияния с сохранённой записью.

В начале файла объявлены **свои исключения сервиса**:

```python
class ServiceError(Exception):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message)
        self.message = message
        self.field = field


class NotFoundError(ServiceError):
    pass


class ConflictError(ServiceError):
    pass


class EmptyUpdateError(ServiceError):
    pass


class RuleViolationError(ServiceError):
    pass
```

Иерархия своих исключений: общий предок `ServiceError` хранит текст и, если ошибка
относится к полю, имя поля. Наследники ничего не добавляют, их смысл в **типе**: по типу
обработчик в `errors.py` понимает, что случилось. HTTP-кодов в классах нет. Исключения —
часть того, что сервис обещает вызывающему коду («могу не найти студента», «ИСУ занят»),
поэтому они объявлены там же, где сервис. Они ни от чего, кроме встроенного `Exception`,
не зависят, и `service.py` не тянет за собой FastAPI.

```python
EARLIEST_CHECK_IN = date(2000, 1, 1)
MAX_STAY_YEARS = 9

FILTER_CHECKS = {
    "full_name": lambda student, value: value.casefold() in student["full_name"].casefold(),
    "group": lambda student, value: student["group"] == value,
    "dormitory": lambda student, value: student["dormitory"] == value,
    "room": lambda student, value: student["room"] == value,
    "is_foreign": lambda student, value: student["is_foreign"] == value,
    "living": lambda student, value: (student["check_out"] is None) == value,
}
```

Словарь «имя фильтра → функция проверки». `lambda student, value: ...` — короткая
безымянная функция из одного выражения. Функции в Python — обычные значения, их можно
класть в словарь. `casefold()` — «регистронезависимое» приведение, более тщательное, чем
`lower()` (например, немецкое `ß` → `ss`). `living`: студент проживает, если
`check_out is None`, и сравниваем это с тем, что попросили.

```python
def add_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        return day.replace(year=day.year + years, day=28)
```

Прибавить годы — значит поменять год. Единственная ловушка — 29 февраля: в невисокосном году
такого дня нет, `replace` бросит `ValueError`, и мы берём 28 февраля. 29.02.2024 + 9 лет =
28.02.2033. Та же логика повторена в `form.js` для атрибута `max`.

```python
def check_dates(check_in: date, check_out: date | None) -> None:
    latest_check_in = add_years(date.today(), 1)

    if check_in < EARLIEST_CHECK_IN or check_in > latest_check_in:
        raise RuleViolationError(
            f"Дата заселения — от 01.01.2000 до {latest_check_in:%d.%m.%Y}", "check_in"
        )

    if check_out is None:
        return

    if check_out <= check_in:
        raise RuleViolationError("Дата выселения должна быть позже даты заселения", "check_out")

    latest_check_out = add_years(check_in, MAX_STAY_YEARS)

    if check_out > latest_check_out:
        raise RuleViolationError(
            f"Дата выселения — не позже {latest_check_out:%d.%m.%Y}: проживание не дольше {MAX_STAY_YEARS} лет",
            "check_out",
        )
```

Правила дат. Это бизнес-проверка, а не структурная: результат зависит от сегодняшней даты и от
соседнего поля. `{latest_check_in:%d.%m.%Y}` — f-строка с форматом даты, клиент видит
конкретную границу, например «до 03.10.2027».

```python
def matches(student: dict, conditions: dict) -> bool:
    return all(FILTER_CHECKS[name](student, value) for name, value in conditions.items())
```

Внутри `all(...)` — **генераторное выражение**. `all` берёт проверки по одной и
останавливается на первой ложной: если группа не совпала, остальные фильтры даже не
вычисляются.

```python
class StudentService:
    def __init__(self, repository: StudentRepository):
        self.repository = repository
```

Сервис не создаёт репозиторий сам, а получает его снаружи. Это **внедрение зависимости**
(лекция 4, слайд «Dependency Injection», вариант «Good: dependency is injected from outside»).

```python
    def find(self, filters: StudentFilter) -> list[dict]:
        conditions = filters.model_dump(exclude_none=True)
        found = (student for student in self.repository.list_all() if matches(student, conditions))
        return list(found)
```

- `model_dump(exclude_none=True)` — словарь только из заданных фильтров: `{"group": "M3301", "dormitory": "alp"}`.
  Пустой фильтр `{}` → нет условий → `all()` от пустого набора равно `True` → проходят все.
- `found` — генератор: в этот момент ещё **ничего** не отфильтровано, это «обещание»
  перебрать список. Работа выполняется в `list(found)`. Одна и та же функция обслуживает
  и GET, и QUERY.

```python
    def create(self, data: StudentCreate) -> dict:
        check_dates(data.check_in, data.check_out)
        student = data.model_dump(mode="json")

        if not self.repository.add(student):
            raise ConflictError(f"Студент с ИСУ {data.isu_id} уже есть", "isu_id")

        return student
```

`model_dump(mode="json")` — **маппинг** (лекция 4, слайд «Mapping»): модель превращается в
обычный словарь, где даты уже строки `"2025-09-01"`. Именно такой словарь лежит в памяти и
в файле. Конфликт относится к полю `isu_id`, чтобы форма показала его под полем ИСУ.

```python
    def update(self, isu_id: str, changes: StudentUpdate) -> dict:
        fields = changes.model_dump(mode="json", exclude_unset=True)

        if not fields:
            raise EmptyUpdateError("Нет полей для обновления")

        def merge(current: dict) -> dict:
            student = {**current, **fields}
            check_out = student["check_out"]
            check_dates(
                date.fromisoformat(student["check_in"]),
                None if check_out is None else date.fromisoformat(check_out),
            )
            return student

        student = self.repository.update(isu_id, merge)

        if student is None:
            raise NotFoundError(f"Студент с ИСУ {isu_id} не найден")

        return student
```

- `exclude_unset=True` — только поля, которые клиент **прислал**. Это отличие PATCH от PUT:
  `{"room": "4021"}` меняет только комнату. Явный `"check_out": null` тоже «прислан» и
  попадёт в `fields`, а `exclude_none` его бы потерял.
- `merge` — функция, объявленная **внутри** метода. Она видит переменную `fields` из
  внешней функции: это **замыкание**, то же самое, что `wrapper` в декораторе (вопрос 8.6).
  Сервис не вызывает её сам, а отдаёт репозиторию, и тот выполняет её под замком
  (раздел 2.4). Так сервис решает, **что** изменить, а репозиторий — **как** сделать это
  без гонки.
- `{**старое, **новое}` — слияние словарей: где ключи совпали, побеждает правый.
- Даты проверяются **после** слияния. Если прислали только `check_out`, сравнивать его надо с
  сохранённым `check_in`. Pydantic этого не может: он видит только тело запроса.
- Если даты не прошли, `RuleViolationError` вылетает из `merge`, проходит через
  `with self.lock` в репозитории (замок освобождается) и доходит до обработчика → 422.
  Запись не изменилась.
- Студента нет → репозиторий вернул `None` → `NotFoundError` → 404.

### 2.7. `routes.py` — контроллер

```python
router = APIRouter(prefix="/api/requests")

IsuPath = Annotated[str, Path(pattern=r"^[0-9]{6}$")]


def get_service(request: Request) -> StudentService:
    return StudentService(request.app.state.repository)


Service = Annotated[StudentService, Depends(get_service)]
```

- `APIRouter(prefix=...)` — набор маршрутов с общим началом пути. Внутри пишем `""` и
  `"/{isu_id}"`, а полный путь получается `/api/requests` и `/api/requests/{isu_id}`.
- `IsuPath` — тип path-параметра: строка из 6 цифр. `/api/requests/abc` даёт 422 ещё до
  вызова обработчика.
- `get_service` — **зависимость**. FastAPI вызывает её на каждый запрос и передаёт объект
  `Request`. Из него через `request.app.state` достаём репозиторий, который `lifespan`
  положил туда при старте. Репозиторий один на всё приложение, а лёгкий объект сервиса
  создаётся на каждый запрос. Это и есть разница между «жизнью приложения» и «жизнью
  запроса» (лекция 5, слайд «Жизнь приложения и жизнь запроса»).
- `Service = Annotated[StudentService, Depends(get_service)]` — сокращение, чтобы не писать
  `Depends` в каждом обработчике.

```python
@router.get("", response_model=list[StudentOut])
def list_students(filters: Annotated[StudentFilter, Query()], service: Service):
    return service.find(filters)


@router.api_route("", methods=["QUERY"], response_model=list[StudentOut])
def query_students(filters: StudentFilter, service: Service):
    return service.find(filters)
```

- `@router.get("")` — **декоратор**. Он регистрирует функцию как обработчик `GET /api/requests`.
- `Annotated[StudentFilter, Query()]` — «собери модель из query-параметров». FastAPI берёт
  `?group=M3301&dormitory=alp`, раскладывает по полям `StudentFilter` и проверяет.
  Так можно с FastAPI 0.115.
- Для QUERY готового декоратора `@router.query` нет, поэтому используется общий
  `@router.api_route(..., methods=["QUERY"])`. Параметр `filters: StudentFilter` без
  `Query()` — модель в FastAPI по умолчанию читается из тела.
- `response_model=list[StudentOut]` — ответ пропускается через Response DTO: лишнее не
  утечёт, даты станут строками.

```python
@router.post("", status_code=201, response_model=StudentOut)
def create_student(student: StudentCreate, service: Service):
    return service.create(student)

@router.delete("/{isu_id}", status_code=204)
def delete_student(isu_id: IsuPath, service: Service) -> None:
    service.delete(isu_id)
```

Код успеха задан в декораторе: 201 «создано» и 204 «нет содержимого». На 204 FastAPI
отправляет пустое тело. Ни в одном обработчике нет `if`: логики в контроллере нет
(антипаттерн «Fat Controller» со слайда «Антипаттерны архитектуры»).

Все обработчики — `def`, а не `async def`. Внутри идёт блокирующая работа: чтение и запись
файла, ожидание замка. FastAPI запускает `def`-обработчики в пуле потоков (в трассировке 500
видно `run_in_threadpool`), поэтому, пока один запрос пишет файл, event loop принимает другие.
Лекция 5, слайд «Правила для FastAPI»: `def` — «безопасный выбор по умолчанию».

### 2.8. `main.py` — сборка приложения

```python
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    repository = StudentRepository()
    repository.load()
    app.state.repository = repository
    yield
```

`lifespan` — код, который выполняется один раз при старте (до `yield`) и один раз при
остановке (после `yield`). Лекция 5, слайд «Старт, запрос, остановка в коде». Здесь мы
читаем файл и кладём репозиторий в `app.state` — общее хранилище объектов приложения.
После `yield` ничего не нужно: файл и так переписывается при каждом изменении.
`lifespan` — единственный `async def` в проекте: FastAPI требует асинхронный
контекст-менеджер. Чтение файла внутри блокирующее, но оно происходит один раз до первого
запроса, когда мешать ещё некому.

```python
app = FastAPI(title="Управление студентами", lifespan=lifespan)

app.add_exception_handler(ServiceError, service_error_handler)
app.add_exception_handler(RequestValidationError, validation_error_handler)
app.add_exception_handler(StarletteHTTPException, http_error_handler)
app.add_exception_handler(Exception, unexpected_error_handler)

app.include_router(router)
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
```

- Обработчик подбирается по классу исключения: для `NotFoundError` сработает обработчик
  `ServiceError`, потому что это его наследник.
- `StarletteHTTPException`, а не `fastapi.HTTPException`: 404 и 405 бросает Starlette, на
  котором построен FastAPI, а `fastapi.HTTPException` — его наследник, так что этот
  обработчик ловит оба.
- **Порядок важен.** Маршрутизатор проверяет пути по очереди. `mount("/")` подходит под
  **любой** путь. Если смонтировать его раньше роутера, `/api/requests` ушёл бы в раздачу файлов.
- `StaticFiles(html=True)` раздаёт файлы из `frontend/`, а на `/` отдаёт `index.html`.
  Фронтенд и API живут на одном адресе `http://localhost:8000`, это один **origin**
  (лекция 3, слайд «Origin»), поэтому CORS не нужен.
- Побочный эффект «ловушки» на `/`: неизвестный адрес `/api/nope` попадает в `StaticFiles`,
  тот не находит файл и бросает 404, а наш обработчик превращает его в единый формат.
  `PUT /api/requests` тоже уходит в `StaticFiles`, а он понимает только GET и HEAD и бросает 405.

### 2.9. Данные и примеры

`data/students.json` — 8 демо-студентов. Все записи проходят собственную валидацию: комнаты
из 4 цифр, группы латиницей, даты в допустимых пределах. Для показа сочетания фильтров
трое из `M3301` живут в `alp`: Иванов и Петрова проживают, Гарсия Лопес выселился и он
иностранец. Поэтому `?group=M3301&dormitory=alp` даёт троих, а QUERY с `is_foreign: false`
и `living: true` — двоих.

`examples/` — тела запросов для curl. В `create.json` специально лишние пробелы в ФИО и
группа строчными (`m3302`): в ответе видно, что сервер их нормализовал.

### 2.10. Фронтенд

#### `js/api.js` (бывший `storage.js`)

Единственный файл, который знает про сервер. Остальные скрипты вызывают его функции, как
в Лабе 1 вызывали функции `storage.js`. Скрипты подключаются обычными `<script>`, без
модулей, поэтому всё объявленное здесь доступно в `list.js`, `form.js` и `info.js`.

```javascript
const API_URL = "/api/requests";
const QUERY_THRESHOLD = 3;
```

Адрес относительный: запрос уйдёт на тот же origin, с которого загружена страница.

```javascript
class ApiError extends Error {
    constructor(status, message, details) {
        super(message);
        this.status = status;
        this.details = details;
    }
}
```

Свой класс ошибки: кроме текста несёт HTTP-статус и массив `details` из единого формата.
По `status` форма решает, куда выводить ошибку.

```javascript
async function request(method, url, body) {
    const options = { method: method };

    if (body !== undefined) {
        options.headers = { "Content-Type": "application/json" };
        options.body = JSON.stringify(body);
    }

    let response;

    try {
        response = await fetch(url, options);
    } catch (error) {
        throw new ApiError(0, "Сервер недоступен. Проверьте, что он запущен, и обновите страницу", []);
    }

    if (!response.ok) {
        throw await readError(response);
    }

    if (response.status === 204) {
        return null;
    }

    return response.json();
}
```

Общая функция для всех запросов (лекция 3, слайды «Fetch API», «Response», «Async/await»).

- `JSON.stringify` превращает объект в JSON-текст. Заголовок `Content-Type: application/json`
  обязателен: без него FastAPI не станет разбирать тело как JSON.
- `fetch` возвращает Promise. `await` ждёт его, не блокируя страницу.
- Важная тонкость: `fetch` **не** бросает исключение на 404 или 500, для него это успешно
  полученный ответ. Исключение бывает только при обрыве сети, его мы превращаем в
  «Сервер недоступен». Ошибочные статусы проверяем сами через `response.ok` (это `true`
  для 200–299).
- `readError` читает тело ошибки в едином формате и собирает из него `ApiError`. Если тело
  не JSON (такого не должно быть, но мало ли), формирует общий текст.
- У ответа 204 тела нет, `response.json()` на нём упал бы, поэтому возвращаем `null`.

```javascript
async function getStudents(filters) {
    const active = {};

    Object.keys(filters).forEach(function (name) {
        if (filters[name] !== "" && filters[name] !== null && filters[name] !== undefined) {
            active[name] = filters[name];
        }
    });

    if (Object.keys(active).length > QUERY_THRESHOLD) {
        return request("QUERY", API_URL, active);
    }

    const query = new URLSearchParams(active).toString();

    return request("GET", query === "" ? API_URL : API_URL + "?" + query);
}
```

Выбор метода по заданию «если количество query-параметров становится слишком большим,
необходимо использовать метод QUERY». Пустые фильтры отбрасываются: сервер на `?group=`
ответил бы 422. До 3 фильтров включительно — GET с параметрами, которые собирает
`URLSearchParams` (лекция 3, слайд «URLSearchParams»; он же кодирует кириллицу и спецсимволы).
Больше трёх — QUERY с JSON-телом. Браузер разрешает `fetch` с методом QUERY: тело запрещено
только у GET и HEAD.

`getStudent`, `createStudent`, `updateStudent`, `deleteStudent` — однострочные обёртки над
`request`. `studentUrl(isu)` пропускает ИСУ через `encodeURIComponent`: ИСУ приходит из
адреса страницы, и строка вида `../..` не должна превратиться в другой путь.

Без изменений остались `DORMITORIES`, `getDormitoryName`, `formatDate`, `formatPeriod`: это
отображение, а не бизнес-логика. `getIdFromUrl` теперь возвращает строку-ИСУ, а не `Number`.

#### `index.html` + `js/list.js`

Форма фильтров — обычная HTML-форма:

```html
<form id="filters" class="filters" method="get" action="index.html">
    <input type="text" id="filter-group" name="group" minlength="5" maxlength="5"
           pattern="[A-Za-z]\d{4}" placeholder="M3301" ...>
    ...
    <button type="submit" class="button-primary">Найти</button>
    <a class="button" href="index.html">Сбросить</a>
</form>
```

Никакого JS для отправки: по «Найти» браузер сам проверит атрибуты (лекция 2,
«Встроенная браузерная валидация») и перейдёт на `index.html?full_name=&group=M3301&...`.
Состояние фильтров живёт в **адресе страницы**: его можно добавить в закладки, переслать,
обновить страницу — фильтр сохранится. Клиент при этом ничего не хранит. «Сбросить» — просто
ссылка на `index.html` без параметров.

```javascript
function readFilters() {
    const params = new URLSearchParams(window.location.search);
    const filters = {};

    FILTER_NAMES.forEach(function (name) {
        const value = (params.get(name) || "").trim();
        filterForm.elements[name].value = value;

        if (value !== "") {
            filters[name] = parseFilterValue(name, value);
        }
    });

    return filters;
}
```

При загрузке страницы `list.js` читает параметры из адреса, подставляет их обратно в поля
формы (иначе после поиска поля были бы пустыми) и собирает объект только из непустых
значений. `parseFilterValue` превращает `"true"`/`"false"` в настоящие `true`/`false`, чтобы
в теле QUERY были булевы значения JSON, а не строки. Для GET `URLSearchParams` всё равно
превратит их обратно в текст.

```javascript
async function loadStudents() {
    try {
        showStudents(await getStudents(currentFilters));
    } catch (error) {
        showMessageRow("Не удалось загрузить список");
        statusLine.textContent = describeError(error);
    }
}
```

Ошибка сервера (например, `?room=0123`, введённое руками в адресную строку) выводится в
строке статуса `#status` над таблицей: текст ошибки и все подсказки из `details`.

```javascript
async function onTableClick(event) {
    if (event.target.tagName !== "BUTTON") {
        return;
    }

    if (!confirm("Удалить студента?")) {
        return;
    }

    statusLine.textContent = "";

    try {
        await deleteStudent(event.target.dataset.id);
    } catch (error) {
        statusLine.textContent = describeError(error);
    }

    await loadStudents();
}
```

Один обработчик на всю таблицу (делегирование событий, как в Лабе 1). После удаления
таблица заново запрашивается **с теми же фильтрами**. Если студента уже удалили в другой
вкладке, сервер ответит 404, мы покажем это в статусе и всё равно обновим список.

Данные в DOM попадают только через `textContent`, `innerHTML = ""` используется лишь для
очистки `tbody`. Если бы в ФИО оказался `<script>`, он показался бы как текст (лекция 2:
`textContent` — безопасно, `innerHTML` — небезопасно).

#### `student-form.html` + `js/form.js`

HTML-атрибуты — первый барьер, `novalidate` не стоит. Пример:

```html
<input type="text" id="room" name="room" required pattern="[1-9]\d{3}" minlength="4" maxlength="4"
       inputmode="numeric" title="Ровно четыре цифры, первая не 0, например 1205">
```

`inputmode="numeric"` показывает цифровую клавиатуру на телефоне, `title` браузер
показывает в подсказке при ошибке. Все `pattern` проверены в режиме флага `v`: в нём
браузеры сейчас компилируют этот атрибут, и дефис внутри `[...]` обязан быть экранирован
(`\-`).

Что удалено из Лабы 1: `validate()` (ФИО из двух слов, правило дат) и `isIsuTaken()`
(уникальность). Это бизнес-правила, теперь они на сервере. Клиент не может знать, свободен
ли ИСУ: другой пользователь мог занять его секунду назад.

Ограничения дат в атрибутах — подсказка для пользователя, а не замена серверной проверки:

```javascript
function applyCheckOutLimits() {
    if (checkInInput.value === "") {
        checkOutInput.removeAttribute("min");
        checkOutInput.removeAttribute("max");
        return;
    }

    checkOutInput.min = addDays(checkInInput.value, 1);
    checkOutInput.max = addYears(checkInInput.value, MAX_STAY_YEARS);
}
```

При каждом изменении даты заселения пересчитываются `min` (на следующий день) и `max`
(+9 лет) у даты выселения. `addYears` повторяет серверное правило про 29 февраля: если месяц
«уехал» (JS превращает 29.02.2033 в 01.03.2033), берётся последний день февраля через
`setUTCDate(0)`. Все вычисления в UTC, чтобы часовой пояс не сдвинул дату на день.
`max` даты заселения (сегодня + 1 год) выставляется один раз при загрузке страницы.

```javascript
async function onSubmit(event) {
    event.preventDefault();
    clearErrors();
    submitButton.disabled = true;

    try {
        if (editId === null) {
            await createStudent(collectData());
        } else {
            await updateStudent(editId, collectData());
        }
    } catch (error) {
        submitButton.disabled = false;
        showServerError(error);
        return;
    }

    window.location.href = "index.html";
}
```

- `submit` срабатывает только если HTML-проверка прошла.
- Без `id` в адресе — POST, с `id` — PATCH. Кнопка блокируется на время запроса, чтобы
  двойной клик не отправил два POST.
- `collectData()` в режиме редактирования не кладёт `isu_id` в тело: сервер ответил бы 422
  «Неизвестное поле». Поле ИСУ при редактировании `readonly`.
- «Ещё проживает» → `check_out: null`.
- Значения отправляются как введены: обрезка пробелов, схлопывание и `upper` у группы —
  забота сервера.

```javascript
function showServerError(error) {
    if ((error.status === 422 || error.status === 409) && error.details.length > 0) {
        showFieldErrors(error.details);
        return;
    }

    errorBox.textContent = error.message;
}
```

422 и 409 с `details` раскладываются под поля. Для каждого элемента `{field, message}` текст
попадает в `#error-<field>`, а поле получает класс `has-error` (толстая рамка, как в Лабе 1).
400, 404, 500 и обрыв сети выводятся в `#form-error`. Если сервер назвал поле, которого нет
в форме, текст тоже идёт в `#form-error`.

Механизм `was-submitted` из Лабы 1 сохранён: подсветка невалидных полей включается только
после первой попытки отправки.

#### `js/info.js`

```javascript
try {
    student = await getStudent(id);
} catch (error) {
    const notFound = error.status === 404 || error.status === 422;
    main.textContent = notFound ? "Студент не найден" : error.message;
    return;
}
```

На 404 (нет такого ИСУ) и 422 (в адресе вообще не ИСУ, например `?id=abc`) пользователь
видит «Студент не найден». Остальные ошибки показываются текстом сервера.

#### `css/styles.css`

Добавлены стили формы фильтров: сетка в 3 колонки на сером фоне `var(--surface)`, при
ширине ≤ 700 px — одна колонка (в том же `@media`, где таблица превращается в карточки).
Строка статуса оформлена как ошибки формы: полужирный текст с `!`, а пустая скрыта через
`:empty`. Новых цветов нет, всё через переменные `:root`.

---

## 3. Путь запроса от кнопки до файла и обратно

Общая схема — лекция 5, слайд «Путь запроса в FastAPI»: ОС → uvicorn (разбор HTTP) →
middleware → Router (путь + метод) → валидация Pydantic → обработчик (наш код) →
сериализация в JSON → HTTP-ответ. «Всё, кроме блока „Обработчик“, за нас делают сервер и
фреймворк».

### 3.1. «Сохранить» в форме добавления

1. **HTML-валидация.** Пользователь нажимает «Сохранить». Браузер проверяет атрибуты:
   `required`, `pattern`, `minlength`, `min`/`max` у дат. Если что-то не так, на поле
   приходит событие `invalid`, `form.js` вешает на форму класс `was-submitted` (поля
   подсвечиваются), браузер показывает подсказку из `title`, и **запрос не уходит**.
2. **`form.js`.** Если всё в порядке, срабатывает `submit` → `onSubmit`:
   - `event.preventDefault()` отменяет обычную отправку формы с перезагрузкой страницы;
   - `clearErrors()` стирает старые ошибки, кнопка блокируется;
   - `collectData()` собирает объект `{isu_id, full_name, group, dormitory, room, check_in, check_out, is_foreign, notes}`.
3. **`api.js`.** `createStudent(data)` → `request("POST", "/api/requests", data)`:
   `JSON.stringify` превращает объект в текст, ставится заголовок `Content-Type: application/json`.
4. **`fetch`.** Браузер видит, что адрес того же origin (`http://localhost:8000`), значит
   CORS и предварительный запрос не нужны. В сеть уходит:
   ```
   POST /api/requests HTTP/1.1
   Host: localhost:8000
   Content-Type: application/json

   {"isu_id":"415100","full_name":"  Тестова   Анна ","group":"m3302",...}
   ```
5. **uvicorn.** Принимает TCP-соединение, разбирает HTTP и вызывает ASGI-приложение
   `app(scope, receive, send)`. В `scope` лежат метод, путь и заголовки (слайд «ASGI:
   приложение — это корутина»).
6. **Router.** Starlette по очереди сверяет маршруты с методом и путём и находит
   `POST /api/requests` → `create_student`.
7. **Pydantic.** FastAPI читает тело, разбирает JSON и строит `StudentCreate`:
   - `collapse_spaces` превращает `"  Тестова   Анна "` в `"Тестова Анна"`, `strip_upper`
     превращает `"m3302"` в `"M3302"`;
   - проверяются шаблоны, `Literal`, `StrictBool`, отсутствие лишних полей.

   Ошибка → `RequestValidationError` → `validation_error_handler` → 400 или 422, и
   обработчик вообще не вызывается.
8. **Зависимость.** FastAPI вызывает `get_service(request)`: берёт репозиторий из
   `request.app.state` и создаёт `StudentService`.
9. **`routes.py`.** `create_student` — обычный `def`, поэтому FastAPI запускает его в пуле
   потоков. Он просто вызывает `service.create(student)`.
10. **`service.py`.** `check_dates` проверяет даты (при нарушении будет `RuleViolationError`
    → 422). `model_dump(mode="json")` превращает модель в словарь со строковыми датами.
11. **`repository.py` → Lock → файл.** `add` берёт `self.lock`. Пока замок у этого потока,
    другие потоки ждут на `with`. Внутри:
    - проверка «ИСУ занят?»; если занят → `False` → сервис бросает `ConflictError` → 409;
    - вставка в словарь;
    - `save()`: `json.dumps` и `write_text` перезаписывают `students.json` целиком.

    Потом замок отпускается.
12. **`StudentOut` → 201.** Сервис возвращает словарь. FastAPI пропускает его через
    `response_model=StudentOut`, сериализует в JSON и отвечает с кодом 201 из
    `status_code=201`.
13. **Обратно в браузер.** `fetch` получает ответ, `response.ok === true`, возвращается
    созданный студент. `onSubmit` делает `window.location.href = "index.html"`, это
    **редирект** на список. Список загружается заново и делает свой GET.

Если ИСУ занят, путь меняется на шаге 11: `ConflictError` → `service_error_handler` → 409
с `details: [{"field": "isu_id", ...}]` → `fetch` получает `ok === false` → `readError` → `ApiError`
→ `showServerError` → текст под полем ИСУ.

### 3.2. Фильтр по двум полям (GET)

1. На `index.html` пользователь вводит группу `M3301`, выбирает общежитие «Альпийская» и
   нажимает «Найти».
2. Браузер проверяет атрибуты полей фильтра. Поскольку у формы `method="get"`, он **сам**
   переходит по адресу
   `index.html?full_name=&group=M3301&dormitory=alp&room=&is_foreign=&living=`.
3. `StaticFiles` отдаёт тот же `index.html`: query-параметры статическому серверу не важны.
4. `list.js`, функция `readFilters()`: читает адрес через `URLSearchParams`, возвращает
   значения в поля формы и собирает только непустые → `{group: "M3301", dormitory: "alp"}`.
5. `getStudents(filters)`: 2 фильтра ≤ `QUERY_THRESHOLD` (3) → GET.
   `URLSearchParams` строит строку → `fetch("/api/requests?group=M3301&dormitory=alp")`.
6. Router находит `GET /api/requests` → `list_students`. `Annotated[StudentFilter, Query()]`
   велит FastAPI собрать модель из query-параметров и проверить её: неизвестный параметр
   или `?group=` дали бы 422.
7. `service.find`:
   - `model_dump(exclude_none=True)` → `{"group": "M3301", "dormitory": "alp"}`;
   - `found = (... for student in list_all() if matches(...))` — пока только генератор;
   - `list(found)` прогоняет его: `list_all()` под замком отдаёт снимок списка, для каждого
     студента `all(...)` проверяет оба условия.
8. 200 + массив из трёх студентов (`response_model=list[StudentOut]`).
9. `showStudents` строит строки таблицы через `createElement` и `textContent`.

### 3.3. Фильтр по четырём полям (QUERY)

1. К группе и общежитию добавляем «Иностранец: Нет» и «Проживает сейчас: Да» → «Найти».
2. Адрес страницы: `index.html?full_name=&group=M3301&dormitory=alp&room=&is_foreign=false&living=true`.
3. `readFilters()` → `{group: "M3301", dormitory: "alp", is_foreign: false, living: true}`.
   `parseFilterValue` превратил строки `"false"`/`"true"` в булевы значения.
4. `getStudents`: 4 > 3 → `request("QUERY", "/api/requests", filters)`:
   ```
   QUERY /api/requests HTTP/1.1
   Content-Type: application/json

   {"group":"M3301","dormitory":"alp","is_foreign":false,"living":true}
   ```
5. Router находит маршрут с `methods=["QUERY"]` → `query_students`. Модель `StudentFilter`
   на этот раз читается **из тела** (параметр без `Query()`).
6. Дальше всё то же самое: та же модель, тот же `service.find`, 200 и двое студентов.
7. В DevTools → Network (лекция 1, слайд «Что видно в DevTools Network») видно метод
   `QUERY` и вкладку Payload с JSON.

Если бы фронтенд и API жили на разных origin, этот запрос потребовал бы preflight: QUERY не
входит в «простые» методы GET/HEAD/POST, а `Content-Type: application/json` — не «простой»
тип (лекция 3, слайд «Simple и Preflight Requests»). У нас один origin, и preflight не нужен.

### 3.4. Удаление

1. Пользователь нажимает «Удалить» в строке таблицы. Срабатывает один общий обработчик
   `onTableClick` на `#students-table` (делегирование: кнопка не имеет своего обработчика,
   событие «всплывает» до таблицы).
2. `confirm("Удалить студента?")`: «Отмена» → ничего не происходит.
3. `deleteStudent(event.target.dataset.id)` → `fetch("/api/requests/412345", {method: "DELETE"})`.
4. Router → `delete_student`. `IsuPath` проверяет, что в пути 6 цифр.
5. `service.delete` → `repository.delete`: под замком `self.students.pop(isu_id, None)`. Если
   ключа не было → `False` → `NotFoundError` → 404. Иначе `save()` перезаписывает файл → `True`.
6. Обработчик возвращает `None`, FastAPI отвечает **204 No Content** без тела.
7. `request()` в `api.js` видит 204 и возвращает `null`, не пытаясь читать JSON.
8. `loadStudents()` заново запрашивает список **с теми же фильтрами** из адреса страницы —
   таблица перерисована.

---

## 4. API

| Метод | Путь | Тело | Успех | Ошибки |
|---|---|---|---|---|
| GET | `/api/requests` | — | 200, массив | 422 (плохой фильтр, лишний параметр) |
| GET | `/api/requests/{isu_id}` | — | 200, студент | 404, 422 (не 6 цифр) |
| POST | `/api/requests` | `StudentCreate` | 201, студент | 400, 409, 422 |
| PATCH | `/api/requests/{isu_id}` | `StudentUpdate` | 200, студент | 400 (пусто), 404, 422 |
| DELETE | `/api/requests/{isu_id}` | — | 204 | 404, 422 |
| QUERY | `/api/requests` | `StudentFilter` | 200, массив | 400, 422 |

Неверный метод для существующего адреса — 405, неизвестный адрес — 404, сбой сервера — 500.

**GET списка с фильтром**

```
GET /api/requests?group=M3301&living=true
→ 200
[{"isu_id": "412345", "full_name": "Иванов Иван Иванович", "group": "M3301", "dormitory": "alp",
  "room": "1205", "check_in": "2024-09-01", "check_out": null, "is_foreign": false, "notes": ""},
 {"isu_id": "412346", "full_name": "Петрова Анна Сергеевна", ...}]
```

**GET одного студента**

```
GET /api/requests/412345
→ 200
{"isu_id": "412345", "full_name": "Иванов Иван Иванович", "group": "M3301", ...}

GET /api/requests/999999
→ 404
{"error": {"status": 404, "code": "NOT_FOUND", "message": "Студент с ИСУ 999999 не найден", "details": []}}
```

**POST**

```
POST /api/requests
Content-Type: application/json

{"isu_id": "415001", "full_name": "  Соколова   Елена  Викторовна ", "group": "m3302",
 "dormitory": "len", "room": "4020", "check_in": "2025-09-01", "check_out": null,
 "is_foreign": false, "notes": "Создана через curl"}

→ 201
{"isu_id": "415001", "full_name": "Соколова Елена Викторовна", "group": "M3302", "dormitory": "len",
 "room": "4020", "check_in": "2025-09-01", "check_out": null, "is_foreign": false,
 "notes": "Создана через curl"}
```

**PATCH**

```
PATCH /api/requests/415001
Content-Type: application/json

{"room": "4021"}

→ 200
{"isu_id": "415001", ..., "room": "4021", ...}
```

`{"check_out": null}` → студент снова «проживает». `{}` → 400 «Нет полей для обновления».

**DELETE**

```
DELETE /api/requests/415001
→ 204 (тела нет)
```

**QUERY**

```
QUERY /api/requests
Content-Type: application/json

{"group": "M3301", "dormitory": "alp", "is_foreign": false, "living": true}

→ 200
[{"isu_id": "412345", ...}, {"isu_id": "412346", ...}]
```

`{}` → все студенты.

**Когда GET, а когда QUERY.** Оба метода безопасные (не меняют данные) и идемпотентные
(повтор даёт тот же результат). Это видно на слайде «Два свойства методов» лекции 1: QUERY
стоит там рядом с GET и в SAFE, и в IDEMPOTENT. Разница в том, где лежат параметры:
- в GET они в URL: адрес удобно сохранить и переслать, но длина URL ограничена, и всё
  приходится кодировать в строку;
- в QUERY они в теле: можно передать много параметров, вложенные структуры, настоящие
  типы JSON.

Клиент использует GET для коротких фильтров (≤ 3) и QUERY для длинных (≥ 4). Сервер
принимает оба варианта с любым числом фильтров.

---

## 5. Валидация

Лекция 4, слайд «Validation: два типа проверки»:
- **Structural Validation** — «проверка структуры и формата данных»: тип, обязательность,
  формат;
- **Business Validation** — «проверка бизнес-правил и ограничений»: «комната уже занята»,
  «дублирующая заявка».

| Поле | HTML (первый барьер) | Сервер | Где на сервере | Код и сообщение |
|---|---|---|---|---|
| `full_name` | `required minlength=5 maxlength=100 pattern=…` (≥ 2 слов) | пробелы по краям убираются, повторные схлопываются; 5–100 символов; ≥ 2 слов из букв, дефис/апостроф внутри слова | `schemas.py`, `FullName` | 422 «ФИО — минимум два слова из букв…» |
| `group` | `required minlength=5 maxlength=5 pattern="[A-Za-z]\d{4}"` | `strip` + `upper`, `^[A-Z][0-9]{4}$` (только латиница) | `schemas.py`, `Group` | 422 «Группа — латинская буква и 4 цифры…» |
| `isu_id` | `required pattern="\d{6}" minlength/maxlength=6`, `readonly` при правке | строка `^[0-9]{6}$`, число → 422 | `schemas.py`, `IsuId`; в пути — `IsuPath` | 422 «ИСУ — строка ровно из 6 цифр…» |
| `isu_id` (повтор) | — | ИСУ свободен | `service.create` + `repository.add` (под замком) | 409 «Студент с ИСУ … уже есть» |
| `isu_id` в PATCH | поле не отправляется | поля нет в `StudentUpdate` | `schemas.py`, `extra="forbid"` | 422 «Неизвестное поле» |
| `dormitory` | `<select required>`, первая опция пустая `disabled` | `Literal["sg","alp","bel","len","msg"]` | `schemas.py`, `DormitoryCode` | 422 «Общежитие — один из кодов…» |
| `room` | `required pattern="[1-9]\d{3}" minlength/maxlength=4` | `^[1-9][0-9]{3}$` | `schemas.py`, `Room` | 422 «Комната — ровно 4 цифры, первая не 0…» |
| `check_in` (формат) | `type="date"` | только строка `ГГГГ-ММ-ДД`, реальная дата | `schemas.py`, `IsoDate` | 422 «Дата заселения — строка в формате ГГГГ-ММ-ДД…» |
| `check_in` (границы) | `min="2000-01-01"`, `max` = сегодня + 1 год (JS) | 01.01.2000 ≤ дата ≤ сегодня + 1 год | `service.check_dates` | 422 «Дата заселения — от 01.01.2000 до …» |
| `check_out` (формат) | `type="date"`, `required`, пока не отмечено «Ещё проживает» | `ГГГГ-ММ-ДД` или `null` | `schemas.py`, `IsoDate \| None` | 422 «Дата выселения — строка ГГГГ-ММ-ДД или null…» |
| `check_out` (границы) | `min` = заселение + 1 день, `max` = заселение + 9 лет (JS) | позже заселения и не позже заселения + 9 лет (29.02 → 28.02); при PATCH — после слияния | `service.check_dates` | 422 «Дата выселения должна быть позже даты заселения» / «… не позже …: проживание не дольше 9 лет» |
| `is_foreign` | `checkbox` | `StrictBool`: `"yes"`, `1`, `"true"` → ошибка | `schemas.py` | 422 «Иностранец — логическое значение true или false» |
| `notes` | `maxlength="500"` | `strip`, ≤ 500, по умолчанию `""` | `schemas.py`, `Notes` | 422 «Заметки — строка не длиннее 500 символов» |
| любое лишнее поле | — | `extra="forbid"` | все модели | 422 «Неизвестное поле» |
| пропущенное обязательное | `required` | поле без значения по умолчанию | `StudentCreate` | 422 «Обязательное поле» |
| тело целиком | — | JSON-объект с `Content-Type: application/json` | FastAPI + `validation_error_handler` | 400 |
| пустой PATCH | — | хотя бы одно поле | `service.update` | 400 «Нет полей для обновления» |

**Фильтры** проверяются той же логикой (`StudentFilter`). Отличие: ФИО можно одним словом
или частью (2–100 символов). Пустое значение (`?group=`) — ошибка 422: клиент пустые фильтры
не отправляет.

**Почему структурная проверка в схемах, а бизнес-правила в сервисе.**
- Схема видит только сам запрос, и это её сила: она описывает форму данных, а FastAPI
  проверяет её автоматически, до вызова нашего кода. Форма данных — часть контракта API,
  она видна в Swagger.
- Бизнес-правилам нужно то, чего в запросе нет:
  - текущая дата («не позже чем через год от сегодня»);
  - содержимое хранилища («ИСУ уже занят»);
  - старая запись (при PATCH `check_out` надо сравнивать с **сохранённым** `check_in`).
- Если бы правило дат жило в схеме, при PATCH `{"check_out": "2020-01-01"}` схема не знала бы
  дату заселения. А сервис после слияния её знает.
- Сервис можно вызвать не только из HTTP: правила, которые лежат в нём, соблюдаются при
  любом способе вызова.

**Зачем проверять на сервере, если браузер уже проверил.** HTML-валидация работает только
для честного пользователя в браузере. Запрос можно отправить curl'ом, из DevTools или
отключив проверку (`form.noValidate = true`). Именно так в браузерном тесте отправлялась
комната `0123` и кириллическая группа: сервер вернул 422, и форма показала подсказки под
полями. Клиент — подсказка для удобства, сервер — граница, которую не обойти.

---

## 6. Коды ответов и формат ошибок

Формат любой ошибки:

```json
{"error": {"status": 422, "code": "VALIDATION_ERROR", "message": "Данные не прошли проверку",
           "details": [{"field": "room", "message": "Комната — ровно 4 цифры, первая не 0, например 1205"}]}}
```

- `status` дублирует HTTP-код, чтобы его было видно в теле;
- `code` — постоянная строка для программ;
- `message` — текст для человека;
- `details` — ошибки по полям; если поля нет, пустой массив.

| Код | Где рождается | Как вызвать (из `backend/`) |
|---|---|---|
| **200** OK | `routes.py`: обработчик вернул данные, код по умолчанию | `curl "http://localhost:8000/api/requests"` |
| **201** Created | `routes.py`, `@router.post(..., status_code=201)` | `curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create.json"` |
| **204** No Content | `routes.py`, `@router.delete(..., status_code=204)` | `curl -i -X DELETE "http://localhost:8000/api/requests/415001"` |
| **400** Bad Request | `errors.validation_error_handler` (тело не разобрать: `json_invalid`, `missing`, не объект); `service.update` → `EmptyUpdateError` → `errors.service_error_handler`; `errors.http_error_handler` (тело не в UTF-8) | `… -d "@examples/broken.json"`; `curl -X PATCH "http://localhost:8000/api/requests/412345" -H "Content-Type: application/json" -d "@examples/empty.json"` |
| **404** Not Found | `service.get/update/delete` → `NotFoundError` → `service_error_handler`; неизвестный адрес: `StaticFiles` бросает `HTTPException(404)` → `http_error_handler` | `curl "http://localhost:8000/api/requests/999999"`; `curl "http://localhost:8000/api/nope"` |
| **405** Method Not Allowed | `StaticFiles` (смонтирован на `/`) принимает только GET/HEAD и бросает `HTTPException(405)` → `http_error_handler` | `curl -X PUT "http://localhost:8000/api/requests"` |
| **409** Conflict | `service.create` → `ConflictError` (когда `repository.add` вернул `False`) → `service_error_handler` | POST `examples/create.json` дважды |
| **422** Unprocessable Content | Pydantic → `RequestValidationError` → `validation_error_handler`; `service.check_dates` → `RuleViolationError` → `service_error_handler` | `… -d "@examples/create_bad_room_zero.json"`; `… -d "@examples/create_bad_check_out_before.json"` |
| **500** Internal Server Error | `errors.unexpected_error_handler`, зарегистрирован на `Exception` | временно `1 / 0` в `get_student`, см. README |

**Почему 422, а не 400, для неверных полей.** 400 означает «запрос сломан, я не понял, что
вы прислали»: битый JSON, нет тела, вместо объекта массив. 422 означает «запрос понятен,
JSON корректный, но значения не подходят». Клиенту это разные ситуации: при 400 чинить
надо код отправки, при 422 — данные в полях. FastAPI по умолчанию отвечает 422 даже на
битый JSON, поэтому эти случаи мы переводим в 400 сами (`is_body_error`).

**Почему пустой PATCH — 400, а не 422.** Ни одно поле не ошибочно, ошибочен запрос
целиком: обновлять нечего.

---

## 7. Что изменилось по сравнению с Лабой 1 и почему

| Было в Лабе 1 | Стало | Почему |
|---|---|---|
| Данные в cookies браузера, нарезка на куски по 3500 символов | Сервер: словарь в памяти + `backend/data/students.json` | Задание: клиент stateless, данные хранит сервер. Пропал лимит 4 КБ на cookie, данные общие для всех браузеров |
| Короткие ключи `fio, grp, isu, dorm, room, from, to, frn, note` | `full_name, group, isu_id, dormitory, room, check_in, check_out, is_foreign, notes` | Короткие ключи экономили место в cookie, которой больше нет. `from` — зарезервированное слово Python (`from x import y`), поле так не назвать. Новые имена совпадают с примером задания `?group=…&dormitory=…` |
| Числовой `id` = `maxId + 1` + отдельное поле ИСУ | Идентификатор — ИСУ, он же в URL: `/api/requests/412345` | Требование 3 задания. ИСУ уже уникален по смыслу, второй идентификатор не нужен. Генерация `id` на клиенте была бизнес-логикой и ломалась бы при двух клиентах |
| Пустая строка `to: ""` = «ещё проживает» | `check_out: null` | В JSON есть `null` — честное «значения нет». Пустая строка была вынужденной экономией места |
| `validate()`: ФИО из двух слов, выселение позже заселения; `isIsuTaken()` | Удалены; правила в `schemas.py` и `service.py` | Бизнес-логика мигрировала на сервер (требование задания). Уникальность клиент проверить не может в принципе: он не видит чужих данных |
| Комната `\d{1,4}[буква]?` (`512`, `512а`) | Ровно 4 цифры, первая не 0 (`1205`) | Точный фильтр по комнате работает, только если у каждой комнаты одна запись. При свободном формате одну и ту же комнату могли записать как `512`, `0512` и `512а`, и фильтр находил бы лишь часть студентов |
| Группа `[A-Za-zА-Яа-я]\d{4}` | Только латиница `[A-Za-z]\d{4}`, сервер приводит к верхнему регистру | Кириллическую «Р» не отличить на глаз от латинской «P»: студент из «Р3213» молча пропадал бы из фильтра «P3213» |
| `storage.js` — работа с cookie | `api.js` — работа с сервером через `fetch` | Тот же принцип: один файл знает, где данные, остальные вызывают его функции |
| Синхронные функции `getStudents()` | `async`-функции, возвращают Promise | Сеть медленная, ждать её надо, не блокируя страницу (лекция 3) |
| Фильтров нет | Форма фильтров, состояние в URL | Требование задания: «фильтрация по свойствам студента» |
| Ошибки валидации — только от `validate()` | Ошибки приходят с сервера (`details`) и выводятся под полями тем же способом (`has-error`, `#error-<поле>`) | Источник правды — сервер |
| `migrateLegacyStudents` | Удалён | Переносить больше нечего |
| Футер «Лабораторная работа №1» | «Лабораторная работа №2» | — |

Что **не** изменилось: три страницы и ссылки `?id=…`, обычные `<script>` без модулей,
`textContent` для данных, палитра в `:root`, `was-submitted`, адаптивная таблица-карточки,
favicon с котиком, отсутствие комментариев в коде.

---

## 8. Ответы на вопросы к защите

Каждый ответ устроен одинаково:
- **Коротко** — что можно сказать вслух за полминуты;
- **Подробно** — теория с примерами;
- **В моём проекте** — где это в коде;
- **Могут спросить** — уточняющие вопросы и ловушки.

### 8.1. Python в серверной веб-разработке

**Коротко.** Бэкенд принимает HTTP-запросы, проверяет данные, выполняет бизнес-логику,
работает с хранилищем и отдаёт ответ. На Python это пишут с помощью фреймворков (FastAPI,
Django, Flask). Сам код приложения сеть не слушает: между сетью и нашим кодом стоит
сервер, который говорит с приложением по стандарту WSGI или ASGI.

**Подробно.**

*Чем занят бэкенд.* Лекция 4, слайд «Актуальность»: запрос → валидация → бизнес-логика →
доступ к данным → ответ. Большую часть времени бэкенд ничего не считает, а **ждёт**: ответа
базы, чтения файла, другого сервиса. Такие задачи называются I/O-bound (лекция 5, слайд
«I/O-bound и CPU-bound»). Для них скорость самого языка почти не важна: ускоряет то, что
сервер делает, пока ждёт. Поэтому медленный по вычислениям Python хорошо подходит для веба.

*Сервер ≠ фреймворк* (лекция 5, одноимённый слайд):

| | WSGI (синхронный) | ASGI (асинхронный) |
|---|---|---|
| Фреймворки | Flask, Django / DRF | FastAPI, Starlette |
| Серверы | gunicorn, waitress | uvicorn, hypercorn |
| Приложение — это | функция `app(environ, start_response)` | корутина `async app(scope, receive, send)` |
| Один вызов | один запрос от начала до конца | пока запрос ждёт, сервер обслуживает другие |

Минимальное ASGI-приложение без фреймворка (из лекции):

```python
async def app(scope, receive, send):
    if scope["type"] != "http":
        return
    await send({"type": "http.response.start", "status": 200,
                "headers": [(b"content-type", b"text/plain")]})
    await send({"type": "http.response.body", "body": b"hello"})
```

FastAPI — такое же ASGI-приложение, только внутри у него роутинг, валидация,
сериализация и обработка ошибок.

*Почему Python.*
- Плюсы: короткий понятный код, аннотации типов, которые фреймворки превращают в
  валидацию, огромная экосистема (Pydantic, SQLAlchemy, Celery, библиотеки для ML).
- Минусы: вычисления медленнее, чем в компилируемых языках. Из-за GIL потоки одного
  процесса не выполняют Python-код параллельно (вопрос 8.8). Поэтому серверы
  масштабируют процессами-воркерами.

**В моём проекте.**
- Сервер — uvicorn: `uvicorn app.main:app`. `app.main` — модуль `backend/app/main.py`,
  `app` после двоеточия — переменная в нём.
- ASGI-приложение — объект `FastAPI(...)` в `main.py`.
- `uvicorn[standard]` добавляет быстрый разборщик HTTP `httptools` и `watchfiles` для `--reload`.

**Могут спросить.**
- *Чем uvicorn отличается от FastAPI?* — uvicorn принимает TCP-соединения и разбирает HTTP,
  FastAPI решает, какую функцию вызвать, и проверяет данные. Можно заменить uvicorn на
  hypercorn, не меняя ни строчки кода приложения.
- *Python медленный — почему на нём пишут бэкенд?* — Веб в основном ждёт I/O. Тяжёлые
  вычисления выносят в отдельные процессы или сервисы.
- *Что значит `--reload`?* — Сервер следит за файлами и перезапускается при изменении кода.
  Это только для разработки.

### 8.2. Backend-фреймворки Python: FastAPI, Flask, Django REST Framework

**Коротко.**
- **Flask** — микрофреймворк на WSGI: роутинг есть, а валидацию и формат ошибок пишем сами.
- **Django** — фреймворк «всё включено» (ORM, админка, миграции), **DRF** добавляет к нему
  REST-слой: сериализаторы и классы-представления.
- **FastAPI** — ASGI-фреймворк, который по аннотациям типов сам проверяет данные через
  Pydantic и строит документацию.

По варианту у меня FastAPI.

**Подробно.** Сравнение по лекции 5, слайд «Кто что делает за вас»:

| | Flask | Django + DRF | FastAPI |
|---|---|---|---|
| Протокол | WSGI | WSGI | ASGI |
| Сервер в продакшене | gunicorn, waitress | gunicorn, waitress | uvicorn |
| Валидация | вручную (или подключить Pydantic / marshmallow) | Serializer | Pydantic по типам |
| Ошибка валидации | решаете сами | 400 | 422 |
| Параллельность | потоки, процессы | потоки, процессы | event loop + потоки |
| Размер | микро | «всё включено» | средний |

Наш `POST /api/requests` в трёх фреймворках (как на слайдах «Один эндпоинт»):

```python
from flask import Flask, request

app = Flask(__name__)


@app.post("/api/requests")
def create_student():
    data = request.get_json()
    if not isinstance(data, dict) or "isu_id" not in data:
        return {"error": "isu_id is required"}, 422
    if repository.get(data["isu_id"]) is not None:
        return {"error": "exists"}, 409
    return service.create(data), 201
```

Во Flask `request` выглядит как глобальная переменная. Битый JSON — 400 (это делает
`get_json()`). Каждую проверку поля пишем руками. Ответ — кортеж `(тело, код)`.

```python
from rest_framework import serializers
from rest_framework.response import Response
from rest_framework.views import APIView


class StudentIn(serializers.Serializer):
    isu_id = serializers.RegexField(r"^[0-9]{6}$")
    full_name = serializers.CharField(min_length=5, max_length=100)


class Requests(APIView):
    def post(self, request):
        serializer = StudentIn(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = service.create(serializer.validated_data)
        return Response(student, status=201)
```

В DRF HTTP-методы — это методы класса (`get`, `post`, `patch`, `delete`). Сериализатор
описывает и проверяет данные, при ошибке сразу 400 с описанием полей.

```python
@router.post("", status_code=201, response_model=StudentOut)
def create_student(student: StudentCreate, service: Service):
    return service.create(student)
```

В FastAPI проверка описана типом параметра: если тело не подходит под `StudentCreate`,
функция даже не вызывается. 201 задан в декораторе.

Путь запроса тоже разный (лекция 5, слайды «Путь запроса во Flask / в DRF / в FastAPI»):
- во Flask: `before_request` → Router → обработчик → `after_request`;
- в DRF: Middleware Django → URLconf → аутентификация и права → `View` → `Serializer` → `Renderer`;
- в FastAPI: uvicorn → Middleware → Router → валидация Pydantic → обработчик → сериализация.

**В моём проекте.** FastAPI. Он делает за нас:
- разбирает JSON и проверяет его по моделям из `schemas.py`;
- сериализует ответ через `response_model`;
- запускает `def`-обработчики в пуле потоков;
- генерирует Swagger UI на `/docs`.

Самим пришлось написать только формат ошибок (`errors.py`), потому что стандартный ответ
FastAPI `{"detail": [...]}` не подходит под требование единого формата.

**Могут спросить.**
- *Что выбрать для большого проекта с админкой и базой?* — Django + DRF: ORM, миграции и
  админка уже есть.
- *Почему в DRF ошибка валидации 400, а в FastAPI 422?* — Это соглашение фреймворков. 422
  точнее («понял, но данные не подходят»). У нас 422 для полей, а для неразборчивого тела
  мы сами переводим ответ в 400.
- *Откуда берётся Swagger?* — FastAPI строит схему OpenAPI (`/openapi.json`) по аннотациям
  и Pydantic-моделям, а Swagger UI на `/docs` её рисует.
- *Почему в Swagger нет QUERY?* — FastAPI добавляет операцию `query` в `/openapi.json`, но
  схема имеет версию 3.1.0, где такого метода ещё нет, и Swagger UI её просто пропускает
  (проверено: в интерфейсе только GET, POST, GET, PATCH, DELETE). Поэтому QUERY проверяем
  curl'ом и через DevTools.

### 8.3. Типизация данных в Python и аннотации типов

**Коротко.** Python — язык с динамической, но строгой типизацией:
- тип есть у значения, а не у переменной;
- неявных превращений вроде `"1" + 1` нет.

Аннотации (`isu_id: str`, `-> dict | None`) интерпретатор при выполнении **не проверяет**.
Их читают инструменты: IDE, mypy и, главное для нас, FastAPI и Pydantic, которые по ним
проверяют и преобразуют входные данные.

**Подробно.**

```python
def double(x: int) -> int:
    return x * 2

double("ab")
```

Ошибки не будет, результат `"abab"`. Аннотация — это подсказка, а не проверка. Она
сохраняется в объекте функции, и её можно прочитать:

```python
double.__annotations__
```

Результат: `{'x': <class 'int'>, 'return': <class 'int'>}`. Ровно так FastAPI узнаёт, что
нужно обработчику: читает сигнатуру и аннотации.

Конструкции из проекта:

| Запись | Смысл |
|---|---|
| `dict[str, dict]` | словарь: ключи-строки, значения-словари |
| `list[StudentOut]` | список моделей |
| `date \| None` | дата или `None` (то же, что `Optional[date]`) |
| `Literal["sg", "alp", ...]` | одно из конкретных значений |
| `Annotated[str, Field(pattern=...)]` | тип `str` плюс метаданные для Pydantic |
| `StrictBool` | только настоящий `bool`, без превращений |
| `Callable[[dict], dict]` | функция: принимает словарь, возвращает словарь (`change` в `repository.update`) |

Pydantic по умолчанию работает в «мягком» режиме: строку `"5"` для поля `int` он
превратит в число 5. `Strict`-типы это отключают. В JavaScript аннотаций нет вовсе,
TypeScript (лекция 3) добавляет их и проверяет при компиляции, а не во время работы.

**В моём проекте.**
- `schemas.py`: типы полей через `Annotated`, `Literal`, `StrictBool`, `IsoDate | None`.
- `routes.py`: аннотации параметров **управляют** FastAPI. Он смотрит на тип и решает,
  откуда брать значение:
  - `isu_id: IsuPath` берётся из пути;
  - `filters: Annotated[StudentFilter, Query()]` — из query-параметров;
  - `student: StudentCreate` — из тела;
  - `service: Service` — через зависимость.
- `repository.py`: `self.students: dict[str, dict]`, `def get(...) -> dict | None`.

**Могут спросить.**
- *Если передать в `repository.get` число, будет ошибка?* — Python не проверит, просто не
  найдёт ключ. Поэтому типы проверяются на **границе**, в Pydantic: внутрь попадают уже
  правильные данные.
- *Зачем `Annotated`, если можно `Field` в значении по умолчанию?* — Тип с ограничениями
  описывается один раз и переиспользуется в трёх моделях. Явный `null` и «поле не прислали»
  при этом различаются.
- *Чем `Optional[X]` отличается от `X | None`?* — Ничем, второе — новый синтаксис (Python 3.10+).

### 8.4. Модели данных: dataclass, Pydantic-модели, словари и классы

**Коротко.**
- **Словарь** — гибкий, но без гарантий: любые ключи, любые типы.
- **Обычный класс** — данные плюс поведение, но `__init__` и проверки пишутся руками.
- **dataclass** — класс, у которого Python сам генерирует `__init__`, `__repr__`, `__eq__`,
  но типы он **не проверяет**.
- **Pydantic-модель** при создании проверяет и преобразует данные и умеет превращаться в
  JSON и обратно.

На границе API — Pydantic, в хранилище — словари, поведение — в обычных классах.

**Подробно.**

```python
student = {"isu_id": "412345", "full_name": "Иванов Иван"}
student["romm"] = "1205"
```

Опечатка в ключе (`romm`) молча создаёт новое поле.

```python
from dataclasses import dataclass


@dataclass
class Student:
    isu_id: str
    room: str


Student(isu_id=412345, room=None)
```

dataclass создаёт объект без ошибок: аннотации снова только подсказки. Можно добавить
проверки в `__post_init__`, но вручную.

```python
from pydantic import BaseModel, ValidationError


class Student(BaseModel):
    isu_id: str
    room: str


try:
    Student(isu_id=412345, room=None)
except ValidationError as error:
    print(error.error_count())
```

Напечатает `2`: Pydantic нашёл обе ошибки сразу. Ещё он умеет:
- `model_validate(dict)` — построить модель из словаря;
- `model_dump()` — получить словарь обратно;
- `model_dump(mode="json")` — словарь, готовый к `json.dumps` (даты станут строками);
- `model_json_schema()` — схема для Swagger.

| | dict | класс | dataclass | Pydantic |
|---|---|---|---|---|
| Набор полей фиксирован | нет | да | да | да |
| Проверка типов | нет | вручную | нет | да, с понятными ошибками |
| Преобразование (`"2024-09-01"` → `date`) | нет | вручную | нет | да |
| JSON туда и обратно | `json.dumps` | вручную | вручную | встроено |
| Скорость и простота | максимальные | — | высокие | чуть дороже из-за проверок |

**В моём проекте.**
- Pydantic — `schemas.py`: `StudentCreate`, `StudentUpdate` (Request DTO), `StudentOut`
  (Response DTO), `StudentFilter`.
- Словари — `repository.py`: запись студента хранится словарём ровно в том виде, в каком
  лежит в JSON-файле.
- Классы — `StudentService`, `StudentRepository`: в них поведение (методы) и состояние
  (`self.repository`, `self.students`, `self.lock`).
- dataclass в проекте **не используется**: для входных данных нужна проверка (это делает
  Pydantic), а внутренние записи — готовые для JSON словари, и превращать их в объекты
  незачем.

**Могут спросить.**
- *Почему в репозитории словари, а не модели?* — `json.loads` даёт словари, `json.dumps`
  принимает словари, конвертировать не нужно. Данные уже проверены на входе. И репозиторий
  не зависит от `schemas.py`.
- *Чем `model_dump()` отличается от `model_dump(mode="json")`?* — Первый оставит
  `datetime.date(2025, 9, 1)`, второй вернёт `"2025-09-01"`, который можно записать в JSON.
- *Может ли dataclass проверять типы?* — Сам нет. Есть `pydantic.dataclasses.dataclass` —
  dataclass с проверками Pydantic.

### 8.5. Исключения в Python и их обработка в Backend-приложениях

**Коротко.** Исключение — объект-сигнал об ошибке. Оно «всплывает» по стеку вызовов, пока
его не поймает `try/except`. Если не поймать, программа падает. В бэкенде исключения —
часть архитектуры: каждый слой бросает свои, а наверху обработчики превращают их в
HTTP-ответы. Сервер не падает, клиент получает понятную ошибку.

**Подробно.**

```python
try:
    records = json.loads(text)
except json.JSONDecodeError as error:
    raise RuntimeError("Файл повреждён") from error
else:
    print("прочитали без ошибок")
finally:
    print("выполнится в любом случае")
```

- `except` ловит конкретный тип. Голый `except:` поймал бы всё подряд, даже `Ctrl+C`.
- `else` выполняется, если исключения не было, `finally` — всегда.
- `raise ... from error` связывает новое исключение с исходной причиной, в трассировке
  видны обе.

Свои исключения — наследники `Exception`. Обработчик, ловящий базовый класс, ловит и всех
наследников: `except ServiceError` поймает `NotFoundError`.

Лекция 4, слайд «Ошибки как часть архитектуры»: у контроллера свои ошибки (InvalidInput),
у сервиса свои (RoomIsFull), у репозитория свои (StorageError). На слайде лекции 5 «Один
эндпоинт: FastAPI» обработчик бросает `HTTPException(409)`. Мы бросаем свои исключения
**в сервисе**, а HTTP-код им назначает `errors.py`: так сервис не зависит от HTTP.

Путь исключения в нашем проекте:

```
service.get():  raise NotFoundError("Студент с ИСУ 999999 не найден")
  → routes.get_student его не ловит
  → FastAPI/Starlette ищет обработчик по классу: NotFoundError → ServiceError → service_error_handler
  → SERVICE_ERRORS[NotFoundError] = (404, "NOT_FOUND")
  → JSONResponse 404 в едином формате
```

Исключение, на которое нет своего обработчика (например, `ZeroDivisionError`), доходит до
обработчика `Exception` → 500. После ответа Starlette бросает его заново, и uvicorn пишет
трассировку в консоль.

**В моём проекте.**
- `service.py`: иерархия `ServiceError` → `NotFoundError`, `ConflictError`, `EmptyUpdateError`,
  `RuleViolationError` и `raise` при нарушении правил.
- `errors.py`: четыре обработчика, которые превращают исключения в HTTP-ответы.
- `repository.update`: если функция изменения бросила исключение, оно пролетает через
  `with self.lock`, замок освобождается сам, и запись не меняется.
- `repository.load`: `RuntimeError` при битом файле, сервер не стартует.
- `schemas.require_iso_date`: `ValueError`, Pydantic превращает его в ошибку валидации.
- `api.js`: `throw new ApiError(...)`, а `form.js` и `list.js` ловят его в `try/catch`. Это
  тот же механизм в JavaScript.

**Могут спросить.**
- *Что будет без обработчика 500?* — Starlette сам ответит 500, но текстом
  `Internal Server Error`, не в нашем формате.
- *Почему репозиторий возвращает `False` или `None`, а не бросает исключение?* — Для хранилища
  «такого ключа нет» — нормальный результат, а не авария. Что это значит для пользователя
  (404), решает сервис.
- *Почему исключения объявлены в `service.py`, а не в `errors.py`?* — Это часть того, что
  сервис обещает вызывающему коду, как и его методы. `errors.py` зависит от сервиса, а не
  наоборот, поэтому сервис не тянет FastAPI. Лекция 4, слайд «Ошибки как часть архитектуры»:
  бизнес-ошибки — у сервиса.
- *Почему не `raise HTTPException(404)` прямо в сервисе?* — Тогда сервис зависел бы от
  FastAPI, и его нельзя было бы использовать вне HTTP. Слайд «Service не зависит от интерфейса».

### 8.6. Декораторы и их применение в веб-фреймворках

**Коротко.** Декоратор — функция, которая принимает функцию и возвращает функцию: ту же
самую или обёртку над ней. Запись `@d` над `def f` означает `f = d(f)`. Во
веб-фреймворках декораторами:
- регистрируют маршруты (`@router.get`);
- добавляют поведение: логирование, проверку прав, кэш;
- объявляют валидаторы (`@field_validator`) и контекст-менеджеры (`@asynccontextmanager`).

**Подробно.** В Python функция — обычный объект: её можно передать в другую функцию и
вернуть из неё. На этом и держатся декораторы.

Свой декоратор, который замеряет время обработчика:

```python
import functools
import time


def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__}: {time.perf_counter() - start:.3f} c")
    return wrapper


@timed
def find_students():
    ...
```

- `wrapper` — **замыкание**: внутренняя функция помнит `func` из внешней.
- `functools.wraps` копирует в `wrapper` имя, документацию и ссылку на оригинал
  (`__wrapped__`). Для FastAPI это критично: он читает сигнатуру функции, чтобы понять, какие
  у неё параметры. Без `wraps` он увидел бы `wrapper(*args, **kwargs)` и не нашёл бы ни
  `isu_id`, ни тела.

Декоратор с параметрами — это функция, которая **возвращает** декоратор. Так устроен
`@router.get("")`. Упрощённо:

```python
class MiniRouter:
    def __init__(self):
        self.routes = {}

    def get(self, path):
        def decorator(func):
            self.routes[("GET", path)] = func
            return func
        return decorator


router = MiniRouter()


@router.get("/api/requests")
def list_students():
    ...
```

`router.get("/api/requests")` возвращает `decorator`. Тот кладёт функцию в таблицу маршрутов
и возвращает её **без изменений**: функцию можно вызывать напрямую, например в тестах.

Не путать с паттерном **Decorator** из лекции 4 («Decorator, Composite и Bridge»): это
объектная обёртка, которая добавляет объекту новое поведение. Идея та же, но там обёртка
над объектом, а в Python — синтаксис для функций.

**В моём проекте.**
- `routes.py`: `@router.get`, `@router.post`, `@router.patch`, `@router.delete`,
  `@router.api_route(..., methods=["QUERY"])` — регистрация маршрутов. Аргументы
  декоратора (`status_code=201`, `response_model=...`) — настройки маршрута.
- `main.py`: `@asynccontextmanager` превращает генератор `lifespan` в асинхронный
  контекст-менеджер.
- `schemas.py`: `BeforeValidator(...)` — аналог декоратора `@field_validator(..., mode="before")`,
  только в виде метаданных типа:

```python
class StudentCreate(BaseModel):
    full_name: str

    @field_validator("full_name", mode="before")
    @classmethod
    def collapse(cls, value):
        return " ".join(value.split()) if isinstance(value, str) else value
```

Своего декоратора в проекте нет: задаче он не нужен. Но механизм, на котором держатся
декораторы, — замыкание — есть: функция `merge` внутри `service.update` помнит `fields`
из внешней функции и вызывается позже, уже репозиторием под замком.

**Могут спросить.**
- *Что возвращает `@router.get("")`?* — Ту же функцию, только уже зарегистрированную в роутере.
- *В каком порядке применяются несколько декораторов?* — Снизу вверх: ближний к `def`
  применяется первым. В примере выше сначала `@classmethod`, потом `@field_validator`.
- *Зачем `functools.wraps`?* — Чтобы обёртка выглядела как оригинал: имя, документация и
  сигнатура, которую читает FastAPI.

### 8.7. Контекст выполнения запроса и область видимости данных

**Коротко.** Контекст запроса — всё, что относится к текущему запросу: метод, путь,
заголовки, тело, пользователь. В FastAPI обработчик получает это параметрами, а целиком —
объектом `Request`, если его попросить. Данные одного запроса не должны попасть в другой,
поэтому их не кладут в глобальные переменные модуля. Общие долгоживущие объекты создаются
при старте в `lifespan` и лежат в `app.state`.

**Подробно.** Лекция 5, слайд «Контекст запроса»:
- **Flask:** `from flask import request` — выглядит как глобальная переменная, но в каждом
  запросе своя: Flask хранит её в контексте текущего запроса.
- **DRF:** запрос приходит аргументом метода `def post(self, request)`. Пользователь — в
  `request.user` после аутентификации.
- **FastAPI:** фреймворк сам достаёт части запроса и передаёт их параметрами.
  Объект `Request` — если попросить.

Слайд «Жизнь приложения и жизнь запроса» выделяет три уровня:

| Уровень | Сколько живёт | Что там | У нас |
|---|---|---|---|
| Приложение (процесс) | от старта до остановки | настройки, пул соединений, прочитанный JSON | `StudentRepository` и его `Lock` в `app.state` (создаёт `lifespan`) |
| Запрос | от получения запроса до ответа | разобранное тело, сервис, соединение из пула | `StudentService` из `get_service`, модели из тела, локальные переменные обработчика |
| Модуль (константы) | всегда | неизменяемые справочники | `FIELD_HINTS`, `FILTER_CHECKS`, `EARLIEST_CHECK_IN` |

Почему нельзя хранить данные запроса в глобальной переменной:

```python
current_student = None


@router.get("/{isu_id}")
def get_student(isu_id: IsuPath, service: Service):
    global current_student
    current_student = service.get(isu_id)
    return current_student
```

Обработчики работают в разных потоках одновременно. Запрос A записал своего студента,
поток переключился, запрос B записал своего, и A вернёт **чужого** студента. Локальные
переменные функции у каждого вызова свои, они безопасны.

Области видимости в Python (правило LEGB): имя ищется в локальной области функции, потом
в объемлющей (для замыканий), потом в глобальной (модуль), потом во встроенной (`len`,
`print`).

Зависимость с `yield` (слайд «Старт, запрос, остановка в коде») — способ выдать ресурс на
время запроса и гарантированно вернуть его:

```python
def get_conn():
    conn = app.state.pool.acquire()
    try:
        yield conn
    finally:
        conn.release()
```

**В моём проекте.**
- `routes.get_service(request: Request)` берёт `request.app.state.repository`. Это
  единственное место, где обработчики добираются до общего объекта.
- `lifespan` кладёт репозиторий в `app.state` один раз.
- `errors.validation_error_handler` использует контекст: по `request.method` выбирает
  подсказки для фильтров или для формы.
- Единственные общие **изменяемые** данные — `repository.students`, и они защищены `Lock`.

**Могут спросить.**
- *Почему бы не сделать `repository = StudentRepository()` глобальной переменной в
  `routes.py`?* — В одном процессе это работало бы. Но:
  - объект создавался бы при импорте модуля, ещё до запуска сервера;
  - ошибка битого файла вылетала бы при импорте;
  - его время жизни не было бы явно привязано к приложению.

  `lifespan` + `app.state` — способ из лекции.
- *Сервис создаётся на каждый запрос — это не дорого?* — Это один объект с одной ссылкой на
  репозиторий, микросекунды. Зато видно, что у запроса свой сервис, а репозиторий общий.
- *Что будет с `app.state` при 4 воркерах?* — `lifespan` выполнится 4 раза, в каждом
  процессе свой репозиторий (вопрос 8.16).

### 8.8. Синхронный и асинхронный код в Python

**Коротко.** Синхронный код выполняет операции по очереди: на долгой операции (чтение
файла, запрос к базе) поток стоит и ждёт. Асинхронный код (`async`/`await`) на каждом `await`
отдаёт управление **event loop**, и тот, пока операция ждёт, выполняет другие задачи. В
FastAPI:
- `def`-обработчики выполняются в пуле потоков, и блокирующий код в них допустим;
- `async def` выполняются прямо в event loop, внутри можно только `await` асинхронных библиотек.

У нас все обработчики — `def`, потому что внутри работа с файлом и `threading.Lock`.

**Подробно.** Лекция 5, слайд «Процесс, поток, корутина»:

| | Процесс | Поток | Корутина |
|---|---|---|---|
| Память | своя, изолирована | общая с процессом | общая с потоком |
| Кто переключает | ОС | ОС | сам код (`await`) |
| Стоимость | десятки МБ | мегабайт | килобайт |
| Все ядра CPU | да | нет (GIL) | нет |
| В Python | multiprocessing, воркеры сервера | threading | asyncio |

Потоки переключает ОС в любой момент (вытесняющая многозадачность), поэтому возможны гонки
и нужен `Lock`. Корутины переключаются только на `await` (кооперативная), между двумя `await`
никто не вмешается. Но корутина, которая не отдаёт управление (`time.sleep`, долгий
расчёт), останавливает **всех**.

Слайд «Три обработчика в FastAPI», один воркер, по 10 параллельных запросов:

```python
@app.get("/sync")
def sync_handler():
    time.sleep(1)


@app.get("/async-bad")
async def async_bad():
    time.sleep(1)


@app.get("/async-good")
async def async_good():
    await asyncio.sleep(1)
```

| Обработчик | 10 запросов займут | Почему |
|---|---|---|
| `/sync` | ~1 с | каждый запрос в своём потоке из пула |
| `/async-bad` | ~10 с | `time.sleep` блокирует весь event loop, запросы идут по одному |
| `/async-good` | ~1 с | на `await` цикл переключается на следующий запрос |

Вывод слайда: «`async def` сам по себе ничего не ускоряет. Один блокирующий вызов внутри
него делает сервер последовательным».

Правила для FastAPI (одноимённый слайд):
- `def` — обычные библиотеки (`requests`, файлы, синхронный драйвер БД), выполняется в
  пуле потоков, «безопасный выбор по умолчанию»;
- `async def` — только `await` асинхронных библиотек (`httpx`, `asyncpg`). Блокирующее —
  через `await asyncio.to_thread(f)`. `threading.Lock` в `async def` ждать нельзя: пока он
  ждёт, стоит весь цикл, для этого есть `asyncio.Lock`.

GIL (Global Interpreter Lock): в каждый момент Python-код процесса выполняет только один
поток. Пока поток ждёт I/O, GIL отпущен и работают другие. Поэтому потоки ускоряют
ожидание, но не вычисления (слайд «GIL и CPU-задача»: 4 потока — 0.92 с, как и
последовательно, 4 процесса — 0.36 с).

*JavaScript.* Он тоже однопоточный, с event loop (лекция 3, «Event loop», «Promise»,
«Async/await»). `fetch` возвращает Promise, `await` ждёт его, не блокируя страницу.
Отличие от Python (слайд «async/await в Python»): в JS `fetch(url)` без `await` уже
отправляет запрос, а в Python вызов корутины без `await` ничего не запускает.

**В моём проекте.**
- `routes.py`: все 6 обработчиков `def`. В трассировке 500 видно, как FastAPI вызывает
  `def`-обработчик: `run_in_threadpool` → `anyio.to_thread.run_sync`. В пуле по умолчанию
  40 потоков.
- `main.py`: `async def lifespan` — единственный асинхронный код на сервере, потому что
  FastAPI требует асинхронный контекст-менеджер.
- `api.js`: все функции `async`, внутри `await fetch(...)` и `await response.json()`.
  В `form.js` и `list.js` — `await createStudent(...)`, `await getStudents(...)`.

**Могут спросить.**
- *Почему не `async def`, ведь это быстрее?* — Не быстрее само по себе. Внутри у нас
  блокирующие `write_text` и `threading.Lock`: в `async def` они остановили бы весь event loop.
- *Что будет, если в `async def` вызвать `time.sleep(1)`?* — Сервер станет
  последовательным: 10 запросов — 10 секунд (`/async-bad`).
- *В `lifespan` есть блокирующее чтение файла — это плохо?* — Оно выполняется один раз до
  первого запроса, когда ждать нечему. В обработчике запроса так делать было бы нельзя.

### 8.9. Итераторы, генераторы и работа с коллекциями данных

**Коротко.** **Итерируемый** объект — то, что можно перебрать в `for` (список, словарь,
строка, файл). **Итератор** выдаёт элементы по одному через `next()`. **Генератор** —
ленивый итератор: значения вычисляются по требованию, а не заранее. Он экономит память и
позволяет остановиться раньше. Генератор создаётся функцией с `yield` или генераторным
выражением `(x for x in ...)`.

**Подробно.** Что делает `for` под капотом:

```python
numbers = [1, 2, 3]
iterator = iter(numbers)
next(iterator)
next(iterator)
next(iterator)
next(iterator)
```

Три вызова `next` вернут 1, 2, 3, а четвёртый бросит `StopIteration`: `for` ловит это
исключение и заканчивает цикл.

Функция-генератор приостанавливается на `yield` и продолжает со следующего `next()`:

```python
def living(students):
    for student in students:
        if student["check_out"] is None:
            yield student
```

Генераторное выражение — то же самое в одну строку:

```python
squares_list = [x * x for x in range(1_000_000)]
squares_gen = (x * x for x in range(1_000_000))
```

Квадратные скобки создают **список** сразу: миллион чисел в памяти. Круглые создают
**генератор**: ничего не посчитано, пока его не начнут перебирать. Генератор
**одноразовый**: второй проход ничего не выдаст.

Функции, которые читают генератор и останавливаются раньше: `all()` — на первом `False`,
`any()` — на первом `True`, `next()` — на первом элементе.

Коллекции и включения (comprehensions):

```python
{record["isu_id"]: record for record in records}
[describe(error, hints) for error in errors]
```

Первая строка — словарь, вторая — список. Словарь с Python 3.7 сохраняет порядок вставки,
`dict.values()` — «представление» (view), которое меняется вместе со словарём. Поэтому
снимок списка мы делаем через `list(...)`.

**В моём проекте.**
- `service.find`:
  ```python
  found = (student for student in self.repository.list_all() if matches(student, conditions))
  return list(found)
  ```
  Генераторное выражение. Фильтрация выполняется, когда `list()` перебирает генератор.
- `service.matches`: `all(FILTER_CHECKS[name](student, value) for name, value in conditions.items())`.
  Генератор внутри `all`: если первый фильтр не совпал, остальные не вычисляются.
- `repository.load`: включение словаря `{record["isu_id"]: record for record in records}`.
- `repository.list_all`: `list(self.students.values())` — снимок под замком.
- `errors.validation_error_handler`: списковое включение для `details`.
- `main.lifespan` — тоже генератор: `yield` делит его на «старт» и «остановку», а
  `@asynccontextmanager` делает из него контекст-менеджер.

**Могут спросить.**
- *Чем генератор отличается от списка?* — Список хранит все элементы сразу, генератор
  вычисляет их по одному по запросу и проходится один раз.
- *Почему `find` возвращает список, а не генератор?* — Ответ всё равно нужно сериализовать
  целиком. Список можно перебрать несколько раз и узнать его длину, генератор — нет. Генератор
  здесь нужен для самой фильтрации.
- *Что будет, если перебрать генератор второй раз?* — Ничего: он уже исчерпан, цикл не
  выполнится ни разу.

### 8.10. Модули, пакеты и разделение Backend-приложения по слоям

**Коротко.** Модуль — один `.py`-файл, пакет — папка с модулями (у нас с `__init__.py`).
`import` загружает модуль один раз и кэширует его. Бэкенд разделён на слои по
ответственности:
- контроллер (`routes.py`) — принимает HTTP;
- сервис (`service.py`) — правила;
- репозиторий (`repository.py`) — данные;
- отдельно схемы (`schemas.py`) и ошибки (`errors.py`).

Это обязательное требование 5. Зависимости направлены строго сверху вниз.

**Подробно.**

```python
from app.service import StudentService
```

Это абсолютный импорт: пакет `app`, модуль `service`, имя `StudentService`. Python ищет
пакет `app` в списке путей `sys.path`, в который uvicorn добавляет текущую папку. Поэтому
сервер запускается **из `backend/`**. Из корня проекта получится
`ModuleNotFoundError: No module named 'app'` (проверено). При первом импорте модуль
выполняется целиком и кладётся в `sys.modules`, повторный `import` берёт его оттуда.

Почему слои (лекция 4):
- «Separation of Concerns» — каждый слой отвечает за одно;
- «High Cohesion + Low Coupling» — внутри слоя всё про одно, между слоями минимум связей.

Отсюда:
- можно заменить JSON-файл на PostgreSQL, переписав только `repository.py`;
- можно поменять формат ошибок, не трогая бизнес-правила;
- сервис можно вызвать не из HTTP, а из консоли.

Антипаттерны (слайд «Антипаттерны архитектуры»):
- **Fat Controller** — вся логика в обработчике маршрута. У нас в `routes.py` ни одного `if`.
- **God Service** — один сервис делает всё. У нас он только про студентов.
- **Circular Dependencies** — модули импортируют друг друга по кругу. У нас стрелки только вниз:
  `repository.py` не импортирует ничего из проекта.
- **Overengineering** (одноимённый слайд) — лишние слои ради слоёв. Мы **не** заводили
  интерфейс репозитория, фабрики, мапперы: один репозиторий, одна реализация.

Организация по слоям (layer-based) против организации по фичам (feature-based, слайды
«Организация проекта»). У нас одна сущность — студент, поэтому по слоям проще.

**В моём проекте.** Пакет `backend/app/`. Таблица «кто что импортирует» — в разделе 2.2.
Направление: `main → routes → service → repository`; `schemas` и `errors` — общие
«справочные» модули.

**Могут спросить.**
- *Зачем пустой `__init__.py`?* — Он явно делает папку пакетом. С Python 3.3 без него тоже
  заработает (namespace package), но явный вариант понятнее и привычнее инструментам.
- *Почему сервис не импортирует FastAPI?* — Бизнес-логика не должна зависеть от способа
  доставки запроса (слайд «Service не зависит от интерфейса»). Поэтому даже свои исключения
  сервис объявляет у себя, а не в `errors.py`, который импортирует FastAPI. Проверка: после
  `import app.service` модуля `fastapi` в `sys.modules` нет.
- *Что будет, если `repository.py` импортирует `service.py`?* — Циклический импорт: один из
  модулей окажется недогруженным, и Python выдаст `ImportError`. Это признак сломанного
  направления зависимостей.

### 8.11. REST и RESTful API

**Коротко.** REST — архитектурный стиль API:
- всё — **ресурсы** со своими адресами (URI);
- действия над ними выражаются стандартными **методами** HTTP;
- данные передаются **представлениями** (у нас JSON);
- сервер **не хранит состояние клиента** между запросами (stateless);
- результат сообщается кодом ответа.

RESTful API — API, которое этим правилам следует.

**Подробно.** Ограничения REST (Р. Филдинг, 2000):
1. клиент — сервер: интерфейс и хранение разделены;
2. stateless: каждый запрос содержит всё нужное;
3. кэшируемость: ответ сообщает, можно ли его кэшировать;
4. единообразный интерфейс: ресурсы адресуются URI, изменяются через представления,
   сообщения самоописательны (метод, `Content-Type`, код), в идеале со ссылками на
   связанные ресурсы (HATEOAS);
5. многоуровневость: между клиентом и сервером могут стоять прокси и балансировщики,
   клиент этого не замечает.

Ресурсы называют существительными во множественном числе, а действие задаёт метод:

| Хорошо (REST) | Плохо (RPC-стиль) |
|---|---|
| `GET /api/requests/412345` | `GET /api/getStudent?id=412345` |
| `DELETE /api/requests/412345` | `POST /api/deleteStudent` |
| `GET /api/requests?group=M3301` | `POST /api/findStudentsByGroup` |

Лекция 1, слайд «Связь между CRUD и HTTP»: Create → POST, Read → GET, Update → PATCH/PUT,
Delete → DELETE.

**В моём проекте.**
- Коллекция `/api/requests` и элемент `/api/requests/{isu_id}`.
- GET/POST/PATCH/DELETE/QUERY.
- JSON-представления, коды 200/201/204/400/404/405/409/422/500.
- Сервер не хранит сессий, клиент не хранит данных.

По шкале зрелости Ричардсона это уровень 2: ресурсы, методы и коды есть, гиперссылок
(HATEOAS) нет.

**Могут спросить.**
- *Почему `/api/requests`, а не `/api/students`?* — Так в задании: каждая запись — заявка
  студента на проживание.
- *Это «настоящий» REST?* — Уровень 2 из 3: нет HATEOAS, то есть ссылок на связанные ресурсы
  в ответах. Для учебного CRUD этого достаточно, большинство публичных API тоже на уровне 2.
- *ИСУ задаёт клиент, тогда почему создание — POST на коллекцию, а не `PUT /api/requests/{isu}`?* —
  `PUT` на конкретный адрес тоже был бы RESTful («создать или заменить»). Задание требует
  `POST /api/requests`, и это классическая форма создания.

### 8.12. HTTP-методы и коды состояния

**Коротко.** Метод говорит, что сделать с ресурсом:
- GET — прочитать;
- POST — создать;
- PUT — заменить целиком;
- PATCH — изменить часть;
- DELETE — удалить;
- QUERY — прочитать с параметрами в теле.

Важные свойства — safe (не меняет данные) и idempotent (повтор даёт тот же итог). Код
ответа говорит, чем кончилось: 2xx успех, 4xx ошибка клиента, 5xx ошибка сервера.

**Подробно.** Лекция 1, слайды «HTTP methods» и «Два свойства методов»:

| Метод | Safe | Idempotent | У нас |
|---|---|---|---|
| GET | да | да | список и один студент |
| HEAD, OPTIONS | да | да | — |
| QUERY | да | да | список с фильтрами в теле |
| POST | нет | нет | создание |
| PUT | нет | да | — |
| PATCH | нет | не обязательно | частичное обновление |
| DELETE | нет | да | удаление |

«POST чаще всего не safe и не idempotent: повтор может создать второй ресурс». У нас повтор
POST с тем же ИСУ даёт 409 — второго студента не будет.

Классы кодов (слайд «HTTP-ответ: статус, заголовки, тело»): 1xx информационные, 2xx успех,
3xx перенаправление, 4xx ошибка клиента, 5xx ошибка сервера.

| Код | Значение | У нас |
|---|---|---|
| 200 OK | успех, в теле результат | GET, PATCH, QUERY |
| 201 Created | ресурс создан | POST |
| 204 No Content | успех, тела нет | DELETE |
| 400 Bad Request | запрос не разобрать | битый JSON, не объект, нет тела, пустой PATCH |
| 404 Not Found | ресурса нет | нет ИСУ, неизвестный адрес |
| 405 Method Not Allowed | метод не поддерживается для адреса | `PUT /api/requests` |
| 409 Conflict | конфликт с текущим состоянием | ИСУ занят |
| 422 Unprocessable Content | понятно, но данные не подходят | ошибки полей и правил дат |
| 500 Internal Server Error | сбой на сервере | непойманное исключение |

401 и 403 (слайд «В чём разница между 401 и 403?») нам не нужны: авторизации нет.

**В моём проекте.** `routes.py` — методы в декораторах, `status_code=201/204`. `errors.py` —
коды ошибок (`SERVICE_ERRORS`, `HTTP_ERRORS`, обработчики).

**Могут спросить.**
- *Чем PATCH отличается от PUT?* — PUT заменяет ресурс **целиком**: непереданные поля
  пропадут или сбросятся. PATCH меняет только переданные поля. У нас `{"room": "4021"}`
  меняет только комнату (`exclude_unset=True` в `service.update`).
- *DELETE идемпотентен, а повторный вызов даёт 404 — противоречие?* — Нет. Идемпотентность
  — про **состояние сервера**: после первого и после второго DELETE студента одинаково нет.
  Код ответа может различаться.
- *Почему POST отвечает 201, а не 200?* — 201 точнее говорит «создан новый ресурс». В теле
  возвращаем созданного студента: клиент видит, как сервер его нормализовал.
- *Почему у DELETE 204, а не 200?* — Возвращать нечего. 204 явно говорит «тела не будет».
- *Почему на 405 нет заголовка `Allow`?* — `PUT /api/requests` целиком подходит под
  смонтированный на `/` `StaticFiles` (а маршрут API подходит только по пути). Starlette
  отдаёт запрос `StaticFiles`, и тот бросает 405 без `Allow`. Код и формат при этом верные.

### 8.13. Маршрутизация, path-параметры и query-параметры

**Коротко.** Маршрутизация — выбор обработчика по методу и пути.
- **Path-параметр** — часть пути, которая указывает **какой** ресурс: `/api/requests/{isu_id}`.
- **Query-параметры** — после `?`, они уточняют запрос: фильтры, сортировка, страница
  (`?group=M3301`).
- HTTP-метод **QUERY** — это другое: метод, у которого параметры лежат в теле.

**Подробно.** Анатомия URL (лекция 1, слайд «Анатомия URL»):

```
http://localhost:8000/api/requests?group=M3301&dormitory=alp#top
схема  хост      порт  путь         query (параметры)        фрагмент
```

Фрагмент `#...` браузер серверу **не отправляет** (слайд «Query и fragment: что увидит
сервер?»). Это якорь на странице.

Как FastAPI выбирает обработчик:
1. Starlette по очереди сверяет каждый маршрут с путём и методом.
2. Полное совпадение → вызвать этот маршрут.
3. Совпал только путь, а метод нет → 405.
4. Ничего не совпало → 404.

`APIRouter(prefix="/api/requests")` добавляет префикс ко всем маршрутам файла,
`app.include_router(router)` подключает их к приложению.

Path-параметр с шаблоном:

```python
IsuPath = Annotated[str, Path(pattern=r"^[0-9]{6}$")]
```

Query-параметры, собранные в модель:

```python
def list_students(filters: Annotated[StudentFilter, Query()], service: Service):
```

Из `?group=m3301&living=true` FastAPI построит `StudentFilter(group="M3301", living=True)`.

Кодирование: в URL нельзя просто так писать кириллицу и спецсимволы, они кодируются как
`%D0%98...`. На клиенте этим занимаются `URLSearchParams` и `encodeURIComponent`, на сервере
FastAPI раскодирует сам.

Лекция 1, слайд «HTTP QUERY и query parameters URL — разные вещи!»:

| | Query-параметры | Метод QUERY |
|---|---|---|
| Что это | часть URL после `?` | отдельный HTTP-метод |
| Где данные | в адресе | в теле запроса |
| Пример | `GET /api/requests?group=M3301` | `QUERY /api/requests` + `{"group": "M3301"}` |
| Ограничения | длина URL, всё строками | тело любого размера, типы JSON |

**В моём проекте.**
- `routes.py`: `prefix`, `""` и `"/{isu_id}"`, `IsuPath`, `Annotated[StudentFilter, Query()]`,
  `api_route(methods=["QUERY"])`.
- `main.py`: `include_router` **до** `mount("/")`, иначе `/` перехватил бы API.
- `list.js`: `location.search` → `URLSearchParams` → фильтры.
- `api.js`: `URLSearchParams` для GET, `encodeURIComponent` для ИСУ в пути.

**Могут спросить.**
- *Когда path, когда query?* — Path — идентичность ресурса («этот студент»), query —
  параметры выборки («студенты, у которых…»).
- *QUERY — это то же самое, что query-параметры?* — Нет: query-параметры — часть URL, QUERY —
  метод с параметрами в теле. Общее только назначение — поиск.
- *Что будет при `/api/requests/` со слешем на конце?* — Маршрута с таким путём нет, запрос
  уйдёт в `StaticFiles`, и тот ответит 404 в едином формате.
- *Что будет с `?group=M3301&group=P3213`?* — Поле `group` у нас одно значение, FastAPI
  возьмёт последнее.

### 8.14. JSON, сериализация и десериализация

**Коротко.** JSON — текстовый формат структурированных данных: объекты, массивы, строки,
числа, `true`/`false`, `null`.
- **Сериализация** — объект → текст: `json.dumps`, `JSON.stringify`, FastAPI при ответе.
- **Десериализация** — текст → объект: `json.loads`, `JSON.parse`, `response.json()`,
  Pydantic при разборе запроса.

Типа «дата» в JSON нет, поэтому даты передаются строками ISO `"2025-09-01"`.

**Подробно.**

| Python | JSON | JavaScript |
|---|---|---|
| `dict` | объект `{}` | `Object` |
| `list`, `tuple` | массив `[]` | `Array` |
| `str` | строка | `string` |
| `int`, `float` | число | `number` |
| `True` / `False` | `true` / `false` | `true` / `false` |
| `None` | `null` | `null` |
| `date` | — (строка `"2025-09-01"`) | — (`Date` нужно создавать самим) |

Лекция 3, слайд «JSON»: «Не все типы данных JSON поддерживает напрямую» и «Валидация
получаемого через fetch JSON обязательна!». На сервере эту валидацию делает Pydantic.

`json.dumps(records, ensure_ascii=False, indent=2)`:
- `ensure_ascii=False` — кириллица пишется буквами, а не `Ива...`;
- `indent=2` — читаемые отступы.

Цепочка в нашем API:

```
запрос:  байты → (FastAPI) json → dict → (Pydantic) StudentCreate (date-объекты)
внутри:  StudentCreate → model_dump(mode="json") → dict со строками-датами → json.dumps → файл
ответ:   dict → (response_model) StudentOut → JSON-текст → байты
```

Заголовок `Content-Type: application/json` говорит, как читать тело. FastAPI 0.142 по
умолчанию разбирает тело как JSON **только** при этом заголовке. Без него тело остаётся
байтами, и мы отвечаем 400.

**В моём проекте.**
- `repository.load` / `save`: `json.loads` / `json.dumps`.
- `schemas.py`: `IsoDate` принимает только строку `ГГГГ-ММ-ДД`.
- `service.py`: `model_dump(mode="json")`, `date.fromisoformat`.
- `routes.py`: `response_model`.
- `api.js`: `JSON.stringify(body)` и `response.json()`.

**Могут спросить.**
- *Почему даты хранятся строками?* — В JSON нет дат. ISO-формат однозначен и сортируется
  как строка.
- *Что делает `ensure_ascii=False`?* — Пишет не-ASCII символы как есть. Файл получается
  читаемым и меньше по размеру.
- *Чем десериализация отличается от валидации?* — Десериализация превращает текст в
  структуру. Валидация проверяет, что структура правильная: `{"room": "0123"}` —
  корректный JSON, но невалидный студент.
- *Что будет без `Content-Type: application/json`?* — 400 «Тело запроса должно быть
  JSON-объектом с заголовком Content-Type: application/json».

### 8.15. Серверная валидация и обработка ошибок

**Коротко.** Сервер проверяет всё, что приходит, независимо от клиента: проверку в
браузере можно обойти. Проверка идёт в два слоя:
- структурная — Pydantic в `schemas.py`;
- бизнес-правила — `service.py`.

Любая ошибка возвращается в едином формате, с подходящим кодом и понятным русским
сообщением, без технических подробностей.

**Подробно.** Полная таблица полей — раздел 5, коды — раздел 6. Принципы:
1. **Не доверять клиенту.** HTML-атрибуты — удобство для человека. curl, Postman и
   DevTools их не соблюдают.
2. **Сначала форма, потом смысл.** Если тело не JSON-объект — 400. Если поля не того
   формата — 422 по каждому полю. Только потом бизнес-правила.
3. **Нормализовать до проверки.** Пробелы и регистр приводятся к одному виду, иначе
   `"Иванов  Иван"` и `" M3301"` оказались бы ошибками или дублями.
4. **Сообщать все ошибки сразу.** Pydantic возвращает список, пользователь исправит всё за
   один раз.
5. **Не раскрывать внутренности.** 500 — общий текст, трассировка только в консоли.
6. **Один формат.** Клиенту достаточно одной функции разбора (`readError` в `api.js`).

**В моём проекте.** `schemas.py`, `service.check_dates`, `service.update` (пустой PATCH),
`repository.add` (уникальность под замком), `errors.py` (формат, подсказки, обработчики).
На клиенте `form.js/showServerError` выводит 422/409 под полями, остальное — в
`#form-error`.

**Могут спросить.**
- *Почему 422, а не 400?* — Раздел 6: 400 — «не понял запрос», 422 — «понял, но данные не
  подходят».
- *Зачем проверять на сервере, если в HTML есть `pattern`?* — `pattern` проверяет только
  браузер, и только если его не отключить. В браузерном тесте форма с `noValidate`
  отправила комнату `0123`, и сервер вернул 422.
- *Почему английские сообщения Pydantic не отдаются клиенту?* — Они технические
  (`String should match pattern '^[1-9][0-9]{3}$'`) и на английском. Пользователю нужна
  подсказка «ровно 4 цифры, первая не 0, например 1205».

### 8.16. Stateless-архитектура

**Коротко.** Stateless — сервер не помнит клиента между запросами: каждый запрос несёт всё
нужное для его обработки. Клиент у нас тоже stateless:
- нет cookies, `localStorage` и `sessionStorage`;
- данные каждая страница берёт с сервера;
- выбранные фильтры живут в адресе страницы;
- бизнес-логика перенесена на сервер.

**Подробно.**

*Как веб «помнит» пользователя* (лекция 1, одноимённый слайд):
- **cookie** — браузер хранит данные и отправляет их с каждым запросом;
- **session** — сервер хранит состояние и связывает его с `session_id` из cookie;
- **token** — клиент передаёт подписанный токен, сервер проверяет подпись.

Сессия — это состояние на сервере. Stateless-подход от неё отказывается.

*Два вида состояния.*
- **Состояние сессии** — «что этот клиент делал до этого»: выбранные фильтры, шаг мастера,
  корзина. В stateless-архитектуре его на сервере нет.
- **Состояние ресурсов** — сами студенты. Оно, конечно, хранится на сервере.

У нас фильтры в URL, сессий нет, а студенты в словаре и в файле.

*Зачем* (лекция 5, слайд «Что из этого следует»): «Любой воркер должен уметь обработать
любой запрос… Тогда воркеры можно добавлять без изменений кода».

*Где мы этому не соответствуем.* Данные лежат в памяти процесса, поэтому работает только
один воркер (слайд «Память и 4 воркера»). В реальной системе состояние выносят в БД или Redis.

*Почему состояние в URL удобно:* страницу с фильтром можно обновить, сохранить в закладки,
переслать, и кнопка «Назад» работает.

**В моём проекте.**
- `api.js` — ни одного обращения к cookies или хранилищу (браузерный тест проверил, что
  `document.cookie`, `localStorage` и `sessionStorage` пусты).
- `list.js` — фильтры из `location.search`.
- `form.js` и `info.js` — ИСУ из `?id=`.
- На сервере нет сессий: каждый запрос самодостаточен.

**Могут спросить.**
- *Сервер хранит студентов в памяти — значит, он не stateless?* — Stateless относится к
  состоянию **клиента** (сессии). Данные ресурсов храниться обязаны. Но так как они в памяти
  процесса, а не во внешней БД, масштабировать воркерами нельзя.
- *Что будет с данными при `--workers 4`?* — Каждый воркер — отдельный процесс со своим
  словарём, `lifespan` прочитает файл 4 раза. POST попадёт в воркер 2, а следующий GET в
  воркер 3 вернёт 404 (слайд «Память и 4 воркера»). Хуже того, каждый воркер переписывает
  файл **своим** словарём и затирает чужие изменения. `threading.Lock` не поможет: он
  работает только внутри одного процесса.
- *Где хранится, какие фильтры выбраны?* — Только в адресе страницы.

### 8.17. Хранение и фильтрация данных в памяти и JSON-файлах

**Коротко.**
- В памяти — быстро, но данные пропадают при перезапуске и у каждого процесса свои.
- JSON-файл — копия на диске, которая переживает перезапуск.

Мы совмещаем: словарь в памяти — рабочая копия; при старте он загружается из файла в
`lifespan`, а после каждого изменения файл переписывается целиком под `threading.Lock`.
Фильтрация — проход по словарю генераторным выражением.

**Подробно.**

Цикл жизни данных:

```
старт:      lifespan → repository.load() → json.loads(файл) → self.students
чтение:     with lock: list(self.students.values())   (файл не читается)
изменение:  with lock: изменить self.students → save() → json.dumps → файл целиком
PATCH:      with lock: взять запись → change(запись): слить + проверить даты → save()
```

*Зачем `Lock`.* Обработчики `def` работают в разных потоках. Лекция 5, слайд «Гонка при
записи в JSON-файл»:
- два потока прочитали одно значение, и одно обновление потеряно;
- поток может прочитать файл, записанный наполовину, — `JSONDecodeError`, 500.

`with lock:` делает «прочитать — изменить — записать» одним шагом: пока один поток внутри,
остальные ждут.

*Почему GIL не спасает.* GIL гарантирует, что одновременно выполняется одна инструкция
байткода, но поток могут переключить **между** инструкциями: между «проверил, что ИСУ
свободен» и «записал». Запись файла — системный вызов, на время которого GIL отпускается.
В Python 3.13–3.14 есть сборка вообще без GIL (слайд «Python без GIL»), и там «гонки никуда
не деваются: Lock нужен так же».

*Почему `Lock`, а не `RLock`, и почему нет deadlock.* Замок один, его берут только
публичные методы репозитория, а `save()` его не берёт и вызывается только под ним.
Повторного захвата нет, и `RLock` не нужен (слайд «RLock»). Замок всего один, поэтому
deadlock из-за разного порядка захвата невозможен (слайд «Как не попасть в deadlock»:
«По возможности обходиться одним локом»).

*Цена решения.*
- Каждое изменение переписывает весь файл. Для сотен и тысяч записей это незаметно, для
  миллионов нужна база данных.
- Поиск по ИСУ мгновенный (ключ словаря), фильтрация — проход по всем записям.
- Если процесс упадёт посреди записи, файл может оказаться обрезанным. Тогда сервер при
  следующем старте **откажется запускаться** и назовёт файл. Данные не будут молча
  заменены пустым списком. Атомарную запись (временный файл + `os.replace`) мы сознательно
  не делали: в задании этого нет.

**В моём проекте.** `repository.py` целиком, `main.lifespan`, `service.find` и
`service.matches`, `data/students.json`.

Проверено:
- после перезапуска созданный студент на месте;
- отсутствующий файл создаётся с `[]`;
- при битом файле сервер не стартует, а файл остаётся нетронутым;
- 20 одновременных POST с одним ИСУ → ровно один 201.

**Могут спросить.**
- *Зачем `Lock`, если есть GIL?* — См. выше: GIL защищает интерпретатор, а не наши
  многошаговые операции.
- *Зачем замок на чтение?* — Если перебирать словарь циклом, пока другой поток добавляет
  ключ, Python бросит `RuntimeError: dictionary changed size during iteration`. Сам
  `list(d.values())` в обычном CPython под GIL выполняется за один шаг, но без GIL этой
  гарантии нет. Замок даёт её явно и всегда.
- *Что будет, если два PATCH к одному студенту придут одновременно?* — Оба изменения
  сохранятся. Второй PATCH ждёт замок, пока первый читает, сливает, проверяет и пишет, и
  потом читает уже обновлённую запись. Раньше чтение и запись были под **разными**
  захватами замка, и одно изменение могло потеряться. Проверено: при частом переключении
  потоков до исправления 1457 потерь из 2000, после — 0 (разделы 1 и 2.4).
- *Почему не читать файл при каждом запросе?* — Медленно, и замок всё равно был бы нужен.
  Файл — для сохранности, память — для скорости.
- *Что будет, если открыть `students.json` в редакторе и поменять руками, пока сервер
  работает?* — Сервер не заметит: он читает файл только при старте. А при следующем
  изменении через API перезапишет файл своим словарём. Править вручную — только при
  остановленном сервере.

### 8.18. CRUD-операции и уникальная идентификация ресурсов

**Коротко.** CRUD — Create, Read, Update, Delete, четыре базовые операции с данными. В
REST они соответствуют POST, GET, PATCH/PUT, DELETE. Чтобы обратиться к конкретной записи,
у неё должен быть уникальный идентификатор. У нас это ИСУ: он уникален, неизменяем и
стоит в URL.

**Подробно.**

| CRUD | HTTP | Адрес | Метод сервиса | Метод репозитория |
|---|---|---|---|---|
| Create | POST | `/api/requests` | `create` | `add` |
| Read (один) | GET | `/api/requests/{isu_id}` | `get` | `get` |
| Read (много) | GET / QUERY | `/api/requests` | `find` | `list_all` |
| Update | PATCH | `/api/requests/{isu_id}` | `update` | `update` |
| Delete | DELETE | `/api/requests/{isu_id}` | `delete` | `delete` |

*Естественный и искусственный ключ.*
- **Естественный** — значение, которое и так уникально в предметной области: ИСУ, номер паспорта.
- **Искусственный** (суррогатный) — специально выданный номер: автоинкремент, UUID.

В Лабе 1 был искусственный `id = maxId + 1`, и выдавал его клиент. Два клиента
одновременно выдали бы одинаковый `id`. Задание требует ИСУ: он уже уникален, и второй
идентификатор не нужен.

*Как обеспечена уникальность.* Проверка «занят ли ИСУ» и вставка выполняются в
`repository.add` под одним `Lock`. Это аналог `PRIMARY KEY` в базе: дубль невозможен даже
при одновременных запросах. Сервис превращает отказ в 409 с подсказкой под полем ИСУ.

*Неизменяемость.* Идентификатор нельзя поменять через PATCH: поля `isu_id` нет в
`StudentUpdate`, попытка даёт 422 «Неизвестное поле». Если бы ИСУ менялся, ссылки
`student-info.html?id=...`, закладки и другие системы указывали бы в пустоту.

**В моём проекте.** `routes.py` (5 маршрутов CRUD + QUERY), `service.py`, `repository.py`
(словарь с ключом ИСУ), `schemas.StudentUpdate` без `isu_id`.

**Могут спросить.**
- *Почему ИСУ — строка, а не число?* — Это идентификатор, а не количество: с ним не делают
  арифметики, у него фиксированная длина, и в общем случае возможен ведущий ноль.
- *А если ИСУ ввели с ошибкой?* — Удалить запись и создать заново. Смена идентификатора —
  отдельная операция, в задании её нет.
- *Что если два администратора одновременно добавят одного студента?* — Один получит 201,
  второй 409. Проверено: 20 параллельных POST → 1 × 201 и 19 × 409.

---

## 9. Как показать работу на защите

**Подготовка (до начала):**
- сервер запущен в терминале: `cd backend`, `.venv\Scripts\activate`, `uvicorn app.main:app --reload`;
- браузер открыт на <http://localhost:8000/>, DevTools → вкладка **Network**, фильтр
  **Fetch/XHR**;
- второй терминал открыт в `backend/`;
- `backend/data/students.json` открыт в редакторе.

**1. Архитектура (≈ 30 с).** Показать папку `backend/app` и сказать: «`routes.py` — только
HTTP, `service.py` — правила, `repository.py` — хранение. Зависимости только вниз, сервис
не знает про FastAPI. Это обязательное требование 5».

**2. Список и фильтры (≈ 1 мин).**
- Обновить страницу: в Network `GET /api/requests` → 200. Данные пришли с сервера, в
  браузере ничего не хранится.
- Ввести группу `M3301`, общежитие «Альпийская» → «Найти». Адрес страницы изменился, в
  Network `GET /api/requests?group=M3301&dormitory=alp`, три студента.
- Добавить «Иностранец: Нет» и «Проживает: Да» → «Найти». В Network метод **QUERY**, на
  вкладке Payload JSON-тело, два студента. Сказать: «Больше трёх фильтров — QUERY, он
  безопасный и идемпотентный, как GET, но параметры в теле».
- «Сбросить».

**3. Форма и ошибки (≈ 1,5 мин).**
- «Добавить студента», ввести комнату `0123` → «Сохранить»: браузер не пускает (HTML-валидация).
- Исправить на `1210`, заполнить остальное, ИСУ `415555` → «Сохранить». В Network
  `POST` → **201**, редирект на список.
- Добавить ещё раз с тем же ИСУ → **409**, сообщение под полем ИСУ: уникальность
  проверяет сервер.
- «Редактировать» этого студента: ИСУ только для чтения, поменять комнату → `PATCH` → 200.
- «Удалить» → подтвердить → `DELETE` → **204**, таблица обновилась.

**4. curl (≈ 1 мин)**, во втором терминале из `backend/` (в PowerShell — `curl.exe`):

```
curl -X QUERY "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/query.json"
curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/create_bad_group.json"
curl -X POST "http://localhost:8000/api/requests" -H "Content-Type: application/json" -d "@examples/broken.json"
curl -X PUT "http://localhost:8000/api/requests"
```

Ожидается: 200 с двумя студентами; 422 с русской подсказкой про группу; 400 «некорректный
JSON»; 405. Обратить внимание: все ошибки в одном формате `{"error": {...}}`.

**5. Данные в файле (≈ 30 с).** Создать студента curl'ом (`examples/create.json`) и показать
его в `students.json`. Остановить сервер (`Ctrl+C`), запустить снова,
`curl "http://localhost:8000/api/requests/415001"` → 200: данные пережили перезапуск.
Сказать: «Каждое изменение пишется в файл под `threading.Lock`. Запускаем без `--workers`:
у каждого воркера была бы своя копия словаря».

**6. Если спросят про 500.** Открыть `errors.py`, функция `unexpected_error_handler`, и
`main.py`, строка `app.add_exception_handler(Exception, ...)`. Клиент получает общий текст,
трассировка — в консоли сервера. Как проверить вживую — в README, пункт 11.

**Самые вероятные вопросы и где ответ:**

| Вопрос | Раздел |
|---|---|
| Чем PATCH отличается от PUT? | 8.12 |
| Почему 422, а не 400? | 6, 8.15 |
| QUERY — то же, что query-параметры? | 8.13 |
| Что будет при `--workers 4`? | 8.16 |
| Зачем Lock, если есть GIL? | 8.17 |
| Что будет при двух одновременных PATCH? | 2.4, 8.17 |
| Почему обработчики `def`, а не `async def`? | 8.8 |
| Где бизнес-логика и почему не в контроллере? | 2.2, 8.10 |
| Как сервис попадает в обработчик? | 2.7, 8.7 |
| Почему данные проверяются и в браузере, и на сервере? | 5 |
