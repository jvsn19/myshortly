import pytest


@pytest.mark.asyncio
async def test_stats_returns_data(client):
    shorten = await client.post("/api/v1/shorten", json={"url": "https://example.com"})
    code = shorten.json()["code"]

    stats = await client.get(f"/api/v1/stats/{code}")
    assert stats.status_code == 200
    data = stats.json()
    assert data["code"] == code
    assert data["original_url"] == "https://example.com/"
    assert data["total_clicks"] == 0


@pytest.mark.asyncio
async def test_stats_includes_redis_clicks(client, fake_redis):
    shorten = await client.post("/api/v1/shorten", json={"url": "https://example.com"})
    code = shorten.json()["code"]

    # Simulate 3 clicks in Redis (not yet flushed to DB)
    await fake_redis.set(f"clicks:{code}", 3)

    stats = await client.get(f"/api/v1/stats/{code}")
    assert stats.json()["total_clicks"] == 3


@pytest.mark.asyncio
async def test_stats_not_found(client):
    response = await client.get("/api/v1/stats/notexist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
