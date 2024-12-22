from fastapi import APIRouter

from lattegallery.core.dependencies import SessionDep
from lattegallery.core.schemas import StatusResponse

status_router = APIRouter(prefix="/status")


@status_router.get("", summary="Получить статус сервера", tags=["Статус"])
def get_status(session: SessionDep) -> StatusResponse:
    return StatusResponse(status="ok")