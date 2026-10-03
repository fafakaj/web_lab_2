from datetime import date

from app.repository import StudentRepository
from app.schemas import StudentCreate, StudentFilter, StudentUpdate


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


def add_years(day: date, years: int) -> date:
    try:
        return day.replace(year=day.year + years)
    except ValueError:
        return day.replace(year=day.year + years, day=28)


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


def matches(student: dict, conditions: dict) -> bool:
    return all(FILTER_CHECKS[name](student, value) for name, value in conditions.items())


class StudentService:
    def __init__(self, repository: StudentRepository):
        self.repository = repository

    def find(self, filters: StudentFilter) -> list[dict]:
        conditions = filters.model_dump(exclude_none=True)
        found = (student for student in self.repository.list_all() if matches(student, conditions))
        return list(found)

    def get(self, isu_id: str) -> dict:
        student = self.repository.get(isu_id)

        if student is None:
            raise NotFoundError(f"Студент с ИСУ {isu_id} не найден")

        return student

    def create(self, data: StudentCreate) -> dict:
        check_dates(data.check_in, data.check_out)
        student = data.model_dump(mode="json")

        if not self.repository.add(student):
            raise ConflictError(f"Студент с ИСУ {data.isu_id} уже есть", "isu_id")

        return student

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

    def delete(self, isu_id: str) -> None:
        if not self.repository.delete(isu_id):
            raise NotFoundError(f"Студент с ИСУ {isu_id} не найден")
