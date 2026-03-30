from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from docker.errors import DockerException
from httpx import ASGITransport, AsyncClient
from neo4j import AsyncDriver, AsyncGraphDatabase, AsyncSession
from testcontainers.neo4j import Neo4jContainer

from bracc.main import app


@pytest.fixture(scope="session")
def neo4j_container() -> Neo4jContainer:  # type: ignore[misc]
    """Start a Neo4j container for integration tests."""
    try:
        container = Neo4jContainer("neo4j:5-community")
        container.start()
    except DockerException as exc:
        pytest.skip(f"Docker daemon unavailable for integration tests: {exc}")
    yield container  # type: ignore[misc]
    container.stop()


@pytest.fixture(scope="session")
def neo4j_uri(neo4j_container: Neo4jContainer) -> str:
    return neo4j_container.get_connection_url()


@pytest.fixture(scope="session")
def neo4j_auth(neo4j_container: Neo4jContainer) -> tuple[str, str]:
    return ("neo4j", neo4j_container.NEO4J_ADMIN_PASSWORD)


@pytest.fixture(scope="session")
async def neo4j_driver(
    neo4j_uri: str, neo4j_auth: tuple[str, str]
) -> AsyncIterator[AsyncDriver]:
    driver = AsyncGraphDatabase.driver(neo4j_uri, auth=neo4j_auth)
    # Apply schema
    schema_path = Path(__file__).parent.parent.parent.parent / "infra" / "neo4j" / "init.cypher"
    if schema_path.exists():
        async with driver.session() as session:
            for statement in schema_path.read_text().split(";"):
                stmt = statement.strip()
                if stmt and not stmt.startswith("//"):
                    await session.run(stmt)
    # Seed dev data
    seed_path = (
        Path(__file__).parent.parent.parent.parent / "infra" / "scripts" / "seed-dev.cypher"
    )
    if seed_path.exists():
        async with driver.session() as session:
            for statement in seed_path.read_text().split(";"):
                stmt = statement.strip()
                if stmt and not stmt.startswith("//"):
                    await session.run(stmt)
    yield driver
    await driver.close()


@pytest.fixture
async def integration_session(neo4j_driver: AsyncDriver) -> AsyncIterator[AsyncSession]:
    async with neo4j_driver.session() as session:
        yield session


@pytest.fixture
async def integration_client(neo4j_driver: AsyncDriver) -> AsyncIterator[AsyncClient]:
    app.state.neo4j_driver = neo4j_driver
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
