import json
import threading
from collections.abc import Callable
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "students.json"


class StudentRepository:
    def __init__(self, path: Path = DATA_FILE):
        self.path = path
        self.students: dict[str, dict] = {}
        self.lock = threading.Lock()

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

    def save(self) -> None:
        records = list(self.students.values())
        self.path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")

    def list_all(self) -> list[dict]:
        with self.lock:
            return list(self.students.values())

    def get(self, isu_id: str) -> dict | None:
        with self.lock:
            return self.students.get(isu_id)

    def add(self, student: dict) -> bool:
        with self.lock:
            if student["isu_id"] in self.students:
                return False
            self.students[student["isu_id"]] = student
            self.save()
            return True

    def update(self, isu_id: str, change: Callable[[dict], dict]) -> dict | None:
        with self.lock:
            current = self.students.get(isu_id)
            if current is None:
                return None
            student = change(current)
            self.students[isu_id] = student
            self.save()
            return student

    def delete(self, isu_id: str) -> bool:
        with self.lock:
            if self.students.pop(isu_id, None) is None:
                return False
            self.save()
            return True
