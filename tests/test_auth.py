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


@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient, tokens: dict[str, str]) -> None:

    first = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})

    assert first.status_code == 200, first.text

    response = await client.post(
        "/auth/refresh", json={"refresh_token": first.json()["refresh_token"]}
    )

    data = response.json()

    assert response.status_code == 200
    assert tokens["refresh_token"] != data["refresh_token"]
    assert data == {"access_token": ANY, "refresh_token": ANY, "token_type": "bearer"}


@pytest.mark.asyncio
async def test_refresh_unknown_token(client: AsyncClient) -> None:

    response = await client.post("/auth/refresh", json={"refresh_token": "unknown-token"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.asyncio
async def test_refresh_rotation(client: AsyncClient, tokens: dict[str, str]) -> None:
    old_token = tokens["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": old_token})

    assert response.status_code == 200, response.text

    reuse = await client.post("/auth/refresh", json={"refresh_token": old_token})

    assert reuse.status_code == 401
    assert reuse.json() == {"detail": "Could not validate credentials"}


@pytest.mark.asyncio
async def test_refresh_reuse_detection(client: AsyncClient, tokens: dict[str, str]) -> None:
    old_token = tokens["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": old_token})

    assert response.status_code == 200, response.text

    data = response.json()

    reuse_old_token = await client.post("/auth/refresh", json={"refresh_token": old_token})

    assert reuse_old_token.status_code == 401
    assert reuse_old_token.json() == {"detail": "Could not validate credentials"}

    use_new_token = await client.post(
        "/auth/refresh", json={"refresh_token": data["refresh_token"]}
    )

    assert use_new_token.status_code == 401
    assert use_new_token.json() == {"detail": "Could not validate credentials"}
