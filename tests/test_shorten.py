import pytest


@pytest.mark.asyncio
async def test_shorten_returns_short_url(client):
    response = await client.post("/api/v1/shorten", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert "short_url" in data
    assert len(data["code"]) == 7
    assert data["short_url"].endswith(data["code"])


@pytest.mark.asyncio
async def test_shorten_invalid_url(client):
    response = await client.post("/api/v1/shorten", json={"url": "not-a-url"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_shorten_different_codes_each_time(client):
    r1 = await client.post("/api/v1/shorten", json={"url": "https://example.com"})
    r2 = await client.post("/api/v1/shorten", json={"url": "https://example.com"})
    assert r1.json()["code"] != r2.json()["code"]
