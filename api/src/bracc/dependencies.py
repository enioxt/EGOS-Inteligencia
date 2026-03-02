import asyncio
import logging
from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession

from bracc.config import settings
from bracc.models.user import UserResponse
from bracc.services import auth_service
from bracc.services.intelligence_provider import IntelligenceProvider, get_default_provider

_logger = logging.getLogger(__name__)
_driver: AsyncDriver | None = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def init_driver(max_retries: int = 30, base_delay: float = 2.0) -> AsyncDriver:
    global _driver
    _driver = AsyncGraphDatabase.driver(
        settings.neo4j_uri,
        auth=(settings.neo4j_user, settings.neo4j_password),
        max_connection_pool_size=50,
        connection_acquisition_timeout=10,
    )
    for attempt in range(1, max_retries + 1):
        try:
            await _driver.verify_connectivity()
            _logger.info("Neo4j connected on attempt %d", attempt)
            return _driver
        except Exception as exc:
            delay = min(base_delay * attempt, 30.0)
            _logger.warning(
                "Neo4j not ready (attempt %d/%d): %s — retrying in %.1fs",
                attempt, max_retries, exc, delay,
            )
            if attempt == max_retries:
                _logger.error("Neo4j unreachable after %d attempts, giving up", max_retries)
                raise
            await asyncio.sleep(delay)
    return _driver


async def close_driver() -> None:
    global _driver
    if _driver is not None:
        await _driver.close()
        _driver = None


async def get_driver(request: Request) -> AsyncDriver:
    driver: AsyncDriver = request.app.state.neo4j_driver
    return driver


async def get_session(
    driver: Annotated[AsyncDriver, Depends(get_driver)],
) -> AsyncGenerator[AsyncSession]:
    async with driver.session(database=settings.neo4j_database) as session:
        yield session


def get_intelligence_provider() -> IntelligenceProvider:
    return get_default_provider()


async def get_current_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse:
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    user_id = auth_service.decode_access_token(token)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await auth_service.get_user_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


async def get_optional_user(
    token: Annotated[str | None, Depends(oauth2_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UserResponse | None:
    if token is None:
        return None
    user_id = auth_service.decode_access_token(token)
    if user_id is None:
        return None
    return await auth_service.get_user_by_id(session, user_id)


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]
