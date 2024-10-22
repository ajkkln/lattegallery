from fastapi import APIRouter, status
from lattegallery.schemas import StatusResponse, AccountRegisterSchema, AccountSchema, Role
status_router = APIRouter(prefix = "/status")
accounts_router = APIRouter(prefix="/accounts")


@status_router.get("", summary= "Получить статус сервера", tags=["Статус"])

def get_status() -> StatusResponse:
    return StatusResponse(status="ok")

@accounts_router.post('/register', summary = 'Регистрация нового аккаунта', status_code = status.HTTP_201_CREATED, tags = ["Аккаунты"])
def register_account(body: AccountRegisterSchema) -> AccountSchema:
    return AccountSchema(
        id = 1,
        login=body.login,
        name=body.name,
        role = Role.USER,
    )

def get_my_account()-> AccountSchema:
    return AccountSchema(
        id = 1,
        login="userl",
        name='aaa',
        role = Role.USER,
    )