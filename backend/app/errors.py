from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.service import ConflictError, EmptyUpdateError, NotFoundError, RuleViolationError, ServiceError

SERVICE_ERRORS = {
    NotFoundError: (404, "NOT_FOUND"),
    ConflictError: (409, "CONFLICT"),
    EmptyUpdateError: (400, "BAD_REQUEST"),
    RuleViolationError: (422, "VALIDATION_ERROR"),
}

HTTP_ERRORS = {
    400: ("BAD_REQUEST", "Некорректный запрос"),
    404: ("NOT_FOUND", "Адрес не найден"),
    405: ("METHOD_NOT_ALLOWED", "Метод не поддерживается для этого адреса"),
}

FIELD_HINTS = {
    "isu_id": "ИСУ — строка ровно из 6 цифр, например \"412345\"",
    "full_name": "ФИО — минимум два слова из букв (внутри слова можно дефис или апостроф), от 5 до 100 символов",
    "group": "Группа — латинская буква и 4 цифры, например M3301",
    "dormitory": "Общежитие — один из кодов: sg, alp, bel, len, msg",
    "room": "Комната — ровно 4 цифры, первая не 0, например 1205",
    "check_in": "Дата заселения — строка в формате ГГГГ-ММ-ДД, например \"2024-09-01\"",
    "check_out": "Дата выселения — строка ГГГГ-ММ-ДД или null, если студент ещё проживает",
    "is_foreign": "Иностранец — логическое значение true или false",
    "notes": "Заметки — строка не длиннее 500 символов",
}

FILTER_HINTS = {
    **FIELD_HINTS,
    "full_name": "ФИО в фильтре — от 2 до 100 символов: буквы, пробел, дефис или апостроф",
    "is_foreign": "Иностранец — true или false",
    "living": "Проживает сейчас — true или false",
}

BODY_ERRORS = {
    "json_invalid": "Тело запроса — некорректный JSON",
    "missing": "Нет тела запроса",
    "model_attributes_type": "Тело запроса должно быть JSON-объектом с заголовком Content-Type: application/json",
    "dict_type": "Тело запроса должно быть JSON-объектом с заголовком Content-Type: application/json",
}


def error_response(status: int, code: str, message: str, details: list | None = None, headers=None) -> JSONResponse:
    content = {"error": {"status": status, "code": code, "message": message, "details": details or []}}
    return JSONResponse(status_code=status, content=content, headers=headers)


def service_error_handler(request: Request, exc: ServiceError) -> JSONResponse:
    status, code = SERVICE_ERRORS[type(exc)]
    details = [] if exc.field is None else [{"field": exc.field, "message": exc.message}]
    return error_response(status, code, exc.message, details)


def is_body_error(error: dict) -> bool:
    if error["type"] == "json_invalid":
        return True
    return tuple(error["loc"]) == ("body",) and error["type"] in BODY_ERRORS


def describe(error: dict, hints: dict) -> dict:
    field = str(error["loc"][-1])

    if error["type"] == "missing":
        message = "Обязательное поле"
    elif error["type"] == "extra_forbidden":
        message = "Неизвестное поле"
    else:
        message = hints.get(field, "Некорректное значение")

    return {"field": field, "message": message}


def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()

    for error in errors:
        if is_body_error(error):
            return error_response(400, "BAD_REQUEST", BODY_ERRORS[error["type"]])

    hints = FILTER_HINTS if request.method in ("GET", "QUERY") else FIELD_HINTS
    details = [describe(error, hints) for error in errors]
    return error_response(422, "VALIDATION_ERROR", "Данные не прошли проверку", details)


def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code, message = HTTP_ERRORS.get(exc.status_code, ("HTTP_ERROR", "Ошибка запроса"))
    return error_response(exc.status_code, code, message, headers=exc.headers)


def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    return error_response(500, "INTERNAL_ERROR", "Внутренняя ошибка сервера. Подробности записаны в консоль сервера")
