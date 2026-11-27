import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_me_without_token(client: AsyncClient) -> None:

    response = await client.get("/users/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.asyncio
async def test_me_with_invalid_token(client: AsyncClient) -> None:

    response = await client.get("/users/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401
    assert response.json() == {"detail": "Could not validate credentials"}


@pytest.mark.asyncio
async def test_me_with_valid_token(
    client: AsyncClient, registered_user: dict[str, str], tokens: dict[str, str]
) -> None:

    response = await client.get(
        "/users/me", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )

    assert response.status_code == 200
    assert response.json()["username"] == registered_user["username"]
    assert "hashed_password" not in response.text
