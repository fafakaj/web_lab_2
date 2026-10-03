import re
from datetime import date
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, StrictBool

DormitoryCode = Literal["sg", "alp", "bel", "len", "msg"]

NAME_WORD = r"[A-Za-zА-ЯЁа-яё]+(?:['\-][A-Za-zА-ЯЁа-яё]+)*"
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def collapse_spaces(value):
    if isinstance(value, str):
        return " ".join(value.split())
    return value


def strip_upper(value):
    if isinstance(value, str):
        return value.strip().upper()
    return value


def strip(value):
    if isinstance(value, str):
        return value.strip()
    return value


def require_iso_date(value):
    if isinstance(value, str) and ISO_DATE.fullmatch(value):
        return value
    raise ValueError("date must be a YYYY-MM-DD string")


IsuId = Annotated[str, Field(pattern=r"^[0-9]{6}$")]
FullName = Annotated[
    str,
    BeforeValidator(collapse_spaces),
    Field(min_length=5, max_length=100, pattern=rf"^{NAME_WORD}(?: {NAME_WORD})+$"),
]
NamePart = Annotated[
    str,
    BeforeValidator(collapse_spaces),
    Field(min_length=2, max_length=100, pattern=r"^[A-Za-zА-ЯЁа-яё' \-]+$"),
]
Group = Annotated[str, BeforeValidator(strip_upper), Field(pattern=r"^[A-Z][0-9]{4}$")]
Room = Annotated[str, Field(pattern=r"^[1-9][0-9]{3}$")]
IsoDate = Annotated[date, BeforeValidator(require_iso_date)]
Notes = Annotated[str, BeforeValidator(strip), Field(max_length=500)]


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


class StudentUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: FullName = None
    group: Group = None
    dormitory: DormitoryCode = None
    room: Room = None
    check_in: IsoDate = None
    check_out: IsoDate | None = None
    is_foreign: StrictBool = None
    notes: Notes = None


class StudentOut(BaseModel):
    isu_id: str
    full_name: str
    group: str
    dormitory: DormitoryCode
    room: str
    check_in: date
    check_out: date | None
    is_foreign: bool
    notes: str


class StudentFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: NamePart | None = None
    group: Group | None = None
    dormitory: DormitoryCode | None = None
    room: Room | None = None
    is_foreign: bool | None = None
    living: bool | None = None
