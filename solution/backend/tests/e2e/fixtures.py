from typing import TYPE_CHECKING, final, Any, Coroutine, Callable
from collections.abc import AsyncIterator

import pytest

from litestar.testing import AsyncTestClient
from sqlalchemy import delete, text
from sqlalchemy.ext.asyncio import AsyncSession

from prodadvert.config import Config
from prodadvert.infrastructure.persistence.database import Base, create_session_maker
from prodadvert.main import get_app

if TYPE_CHECKING:
    from litestar import Litestar

config = Config()
session_maker = create_session_maker(config.postgres)

app = get_app()
app.debug = True

type AppClient = AsyncTestClient[Litestar]


@pytest.fixture(scope="function")
async def test_client() -> AsyncIterator[AppClient]:
    async with AsyncTestClient(app=app) as client:
        yield client


@final
class DBRollback:
    def __init__(self) -> None:
        self._rollbacks: list[tuple[str, type[Base], Any]] = []

    def rollback_id(self, model: type[Base], m_id: Any) -> None:
        if isinstance(m_id, type(...)):
            return
        self._rollbacks.append(("id", model, m_id))

    def rollback_query(self, model: type[Base], where_query) -> None:
        if isinstance(where_query, type(...)):
            return
        self._rollbacks.append(("q", model, where_query))

    def execute(self, raw: str) -> None:
        self._rollbacks.append(("r", Base, raw))

    async def perform_rollbacks(self, session: AsyncSession) -> None:
        for rollback_type, model, query in self._rollbacks:
            if rollback_type == "r":
                await session.execute(text(query))
                continue
            await session.execute(
                delete(model).where(
                    model.id == query  # noqa
                    if rollback_type == "id"
                    else query
                )
            )
        await session.commit()


@pytest.fixture(scope="function")
async def rollback():
    rollback_manager = DBRollback()
    yield rollback_manager
    async with session_maker() as session:
        await rollback_manager.perform_rollbacks(session)


@pytest.fixture(scope="function")
def set_current_day(test_client: AppClient) -> Callable[[int], Coroutine[Any, Any, None]]:
    async def inner(current_day: int) -> None:
        await test_client.post(
            "/time/advance",
            json={"current_date": current_day}
        )
    return inner
