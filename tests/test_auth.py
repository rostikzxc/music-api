import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(
    client: AsyncClient,
) -> None:

    response = await client.post(
        "/auth/register",
        json={
            "username": "test_user",
            "password": "test-password-123",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "test_user"
    assert "hashed_password" not in response.text


@pytest.mark.asyncio
async def test_register_username_taken(
    client: AsyncClient, registered_user: dict[str, str]
) -> None:

    response = await client.post("/auth/register", json=registered_user)

    assert response.status_code == 409
    assert response.json() == {"detail": "Username already taken"}


@pytest.mark.asyncio
async def test_register_username_is_lowercased(client: AsyncClient) -> None:

    response = await client.post(
        "/auth/register",
        json={
            "username": "Test_User",
            "password": "test-password-123",
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "test_user"
