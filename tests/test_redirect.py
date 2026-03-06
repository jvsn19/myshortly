import pytest


@pytest.mark.asyncio
async def test_redirect_to_original_url(client):
    shorten = await client.post("/api/v1/shorten", json={"url": "https://example.com"})
    code = shorten.json()["code"]

    response = await client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com/"


@pytest.mark.asyncio
async def test_redirect_not_found(client):
    response = await client.get("/notexist", follow_redirects=False)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_redirect_increments_click_counter(client, fake_redis):
    shorten = await client.post("/api/v1/shorten", json={"url": "https://example.com"})
    code = shorten.json()["code"]

    await client.get(f"/{code}", follow_redirects=False)
    await client.get(f"/{code}", follow_redirects=False)

    count = await fake_redis.get(f"clicks:{code}")
    assert int(count) == 2


@pytest.mark.asyncio
async def test_redirect_cache_hit(client, fake_redis):
    shorten = await client.post("/api/v1/shorten", json={"url": "https://example.com"})
    code = shorten.json()["code"]

    # First request populates cache
    await client.get(f"/{code}", follow_redirects=False)
    assert await fake_redis.get(f"url:{code}") is not None

    # Second request should still work (cache hit)
    response = await client.get(f"/{code}", follow_redirects=False)
    assert response.status_code == 302
