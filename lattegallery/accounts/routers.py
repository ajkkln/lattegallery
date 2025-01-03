from fastapi import Depends, APIRouter, HTTPException, status
from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import PositiveInt
import jwt
import datetime
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Annotated

from lattegallery.accounts.schemas import (
    AccountCreateSchema,
    AccountPasswordUpdateSchema,
    AccountRegisterSchema,
    AccountSchema,
    AccountUpdateSchema,
    Role,
)
from lattegallery.core.dependencies import AccountServiceDep, SessionDep
from lattegallery.core.schemas import Page, PageNumber, PageSize
from lattegallery.security.dependencies import AuthenticatedAccount, AuthorizedAccount
from lattegallery.security.permissions import Anonymous, Authenticated, IsAdmin
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from pydantic import BaseModel
from lattegallery.accounts.dependencies import get_current_user
from lattegallery.accounts.models import Account
from lattegallery.accounts.services import AccountService , AccountRepository
accounts_router = APIRouter(prefix="/accounts", tags=["Аккаунты"])


@accounts_router.post(
    "/register",
    summary="Регистрация нового аккаунта",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AuthorizedAccount(Anonymous()))],
)
async def register_account(
    body: AccountRegisterSchema, account_service: AccountServiceDep, session: SessionDep
) -> AccountSchema:
    account = await account_service.create(
        AccountCreateSchema(
            login=body.login,
            password=body.password,
            name=body.name,
            role=Role.USER,
        ),
        session,
    )

    return AccountSchema.model_validate(account)


@accounts_router.post(
    "",
    summary="Создать новый аккаунт",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AuthorizedAccount(IsAdmin()))],
)
async def create_account(
    body: AccountCreateSchema,
    current_user: AuthenticatedAccount,
    account_service: AccountServiceDep,
    session: SessionDep,
) -> AccountSchema:
    assert current_user is not None

    if (current_user.role == Role.MAIN_ADMIN and body.role == Role.MAIN_ADMIN) or (
        current_user.role == Role.ADMIN and body.role in {Role.ADMIN, Role.MAIN_ADMIN}
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN)

    account = await account_service.create(body, session)

    return AccountSchema.model_validate(account)


@accounts_router.get(
    "/my",
    summary="Получение данных своего аккаунта",
    dependencies=[Depends(AuthorizedAccount(Authenticated()))],
)
async def get_my_account(account: AuthenticatedAccount) -> AccountSchema:
    return AccountSchema.model_validate(account)


@accounts_router.get("/{id}", summary="Получение аккаунт по идентификатору")
async def get_account_by_id(id: PositiveInt) -> AccountSchema:
    return AccountSchema(
        id=1,
        login="user1",
        name="Вася Пупкин",
        role=Role.USER,
    )


@accounts_router.get("", summary="Получить список всех аккаунтов")
async def get_all_accounts(
    page: PageNumber = 0, size: PageSize = 10
) -> Page[AccountSchema]:
    return Page(
        count=1,
        items=[
            AccountSchema(
                id=1, login="owner", name="Петр Иванов", role=Role.MAIN_ADMIN
            ),
            AccountSchema(id=1, login="admin", name="Иван Петров", role=Role.ADMIN),
            AccountSchema(id=3, login="user1", name="Вася Пупкин", role=Role.USER),
        ],
    )


@accounts_router.put("/my", summary="Обновление данных своего аккаунта")
async def update_my_account(body: AccountUpdateSchema) -> AccountSchema:
    return AccountSchema(
        id=1,
        login="user1",
        name="Вася Пупкин",
        role=Role.USER,
    )


@accounts_router.put("/my/password", summary="Обновить пароль своего аккаунта")
async def update_my_account_password(
    body: AccountPasswordUpdateSchema,
) -> AccountSchema:
    return AccountSchema(
        id=1,
        login="user1",
        name="Вася Пупкин",
        role=Role.USER,
    )


@accounts_router.put("/{id}", summary="Обновить аккаунт по идентификатору")
async def update_account_by_id(
    id: PositiveInt, body: AccountUpdateSchema
) -> AccountSchema:
    return AccountSchema(
        id=1,
        login="user1",
        name="Вася Пупкин",
        role=Role.USER,
    )

@accounts_router.post(
        "",
        summary = "create new account",
        status_code = status.HTTP_201_CREATED,
        dependencies=[Depends(AuthorizedAccount(IsAdmin()))],
)
async def create_account(  
    body: AccountCreateSchema,
    current_user: AuthenticatedAccount,
    account_service: AccountServiceDep,
    session: SessionDep
) -> AccountSchema:
    assert current_user is not None
    if (current_user.role == Role.MAIN_ADMIN and body.role == Role.MAIN_ADMIN) or (current_user.role == Role.ADMIN and body.role in {Role.ADMIN, Role.MAIN_ADMIN}):
        raise HTTPException(status.HTTP_403_FORBIDDEN)


    account = await account_service.create(body, session)
    return AccountSchema.model_validate(account)

@accounts_router.get("/protected", summary="Пример защищенного маршрута")
async def protected_route(current_user: Account = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.name}!"}

SECRET_KEY = "12345" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class User(BaseModel):
    username: str

class UserInDB(User):
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$KIX/6Z0x3T3zG1JZz5g4UuXc9h5sB8U5eB4Q0FQkK7X5A6v6S0x6C",  # password
        "disabled": False,
    }
}


def verify_password(plain_password, hashed_password):
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@app.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(fake_users_db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, token_data.username)
    if user is None:
        raise credentials_exception
    return user


@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

SECRET_KEY = '12345'  
def generate_jwt_token(username):
    
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
 
    payload = {
        'username': username,
        'exp': expiration
    }
  
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token
def decode_jwt_token(token):
    try:
      
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'




security = HTTPBearer()


@app.get("/users/me")
def read_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]
):
    return {"scheme": credentials.scheme, "credentials": credentials.credentials}