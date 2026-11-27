from unittest.mock import ANY

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
async def test_register_username_is_taken(
    client: AsyncClient,
    registered_user: dict[str, str],
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


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, registered_user: dict[str, str]) -> None:

    response = await client.post("/auth/login", data=registered_user)

    assert response.status_code == 200
    assert response.json() == {
        "access_token": ANY,
        "refresh_token": ANY,
        "token_type": "bearer",
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("password", "invalid-test-password-123"),
        ("username", "invalid_test_user"),
    ],
    ids=["wrong_password", "unknown_user"],
)
async def test_login_invalid_credentials(
    client: AsyncClient,
    registered_user: dict[str, str],
    field: str,
    value: str,
) -> None:
    data = {**registered_user, field: value}

    response = await client.post("/auth/login", data=data)

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid username or password"}
