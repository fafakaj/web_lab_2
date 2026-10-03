from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from app.schemas import StudentCreate, StudentFilter, StudentOut, StudentUpdate
from app.service import StudentService

router = APIRouter(prefix="/api/requests")

IsuPath = Annotated[str, Path(pattern=r"^[0-9]{6}$")]


def get_service(request: Request) -> StudentService:
    return StudentService(request.app.state.repository)


Service = Annotated[StudentService, Depends(get_service)]


@router.get("", response_model=list[StudentOut])
def list_students(filters: Annotated[StudentFilter, Query()], service: Service):
    return service.find(filters)


@router.api_route("", methods=["QUERY"], response_model=list[StudentOut])
def query_students(filters: StudentFilter, service: Service):
    return service.find(filters)


@router.get("/{isu_id}", response_model=StudentOut)
def get_student(isu_id: IsuPath, service: Service):
    return service.get(isu_id)


@router.post("", status_code=201, response_model=StudentOut)
def create_student(student: StudentCreate, service: Service):
    return service.create(student)


@router.patch("/{isu_id}", response_model=StudentOut)
def update_student(isu_id: IsuPath, changes: StudentUpdate, service: Service):
    return service.update(isu_id, changes)


@router.delete("/{isu_id}", status_code=204)
def delete_student(isu_id: IsuPath, service: Service) -> None:
    service.delete(isu_id)
