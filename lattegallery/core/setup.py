from contextlib import asynccontextmanager
from typing import cast

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from lattegallery.accounts.repository import AccountRepository
from lattegallery.accounts.routers import accounts_router
from lattegallery.accounts.services import AccountsCreator, AccountService
from lattegallery.core.db import DatabaseManager
from lattegallery.core.routers import status_router
from lattegallery.core.settings import AppSettings
from lattegallery.pictures.repositories import PictureRepository
from lattegallery.pictures.routers import pictures_router
from lattegallery.pictures.services import PictureService
from lattegallery.security.dependencies import authenticate_user


def create_app():
    settings = AppSettings()

    app = FastAPI(
        title="LatteGallery",
        dependencies=[Depends(authenticate_user)],
        lifespan=_app_lifespan,
        servers=[{"url":"http://localhost/api"}],
        root_path_in_servers=False,
    )

    app.include_router(status_router)
    app.include_router(accounts_router)
    app.include_router(pictures_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_credentials=True,
    )

    app.state.settings = settings
    app.state.db_manager = DatabaseManager(settings.db_url)

    account_repository = AccountRepository()
    picture_repository = PictureRepository()

    app.state.account_service = AccountService(account_repository)
    app.state.accounts_creator = AccountsCreator(
        settings.initial_accounts, account_repository, app.state.db_manager
    )
    app.state.picture_service = PictureService(picture_repository, account_repository)

    return app


@asynccontextmanager
async def _app_lifespan(app: FastAPI):
    db_manager = cast(DatabaseManager, app.state.db_manager)
    accounts_creator = cast(AccountsCreator, app.state.accounts_creator)

    await db_manager.initialize()
    await accounts_creator.initialize()
    yield
    await accounts_creator.dispose()
    await db_manager.dispose()