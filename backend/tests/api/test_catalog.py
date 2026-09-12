"""
Catalog & Music API Integration Tests
"""
import io
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_genres_crud(client: AsyncClient, admin_token_headers: dict):
    # Create genre as admin
    res = await client.post(
        "/api/v1/genres",
        json={"name": "Synthwave", "slug": "synthwave", "description": "80s synth music"},
        headers=admin_token_headers,
    )
    assert res.status_code == 201
    genre_id = res.json()["data"]["id"]

    # List genres
    res = await client.get("/api/v1/genres")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # Delete genre as admin
    res = await client.delete(f"/api/v1/genres/{genre_id}", headers=admin_token_headers)
    assert res.status_code == 204


@pytest.mark.asyncio
async def test_artists_and_albums(client: AsyncClient, admin_token_headers: dict):
    # Create Artist
    res = await client.post(
        "/api/v1/artists",
        data={"name": "Daft Punk", "bio": "Electronic duo"},
        headers=admin_token_headers,
    )
    assert res.status_code == 201
    artist_id = res.json()["data"]["id"]

    # List Artists
    res = await client.get("/api/v1/artists?search=Daft")
    assert res.status_code == 200
    assert len(res.json()["data"]) == 1

    # Create Album
    res = await client.post(
        "/api/v1/albums",
        data={"title": "Discovery", "artist_id": str(artist_id), "release_year": "2001"},
        headers=admin_token_headers,
    )
    assert res.status_code == 201
    album_id = res.json()["data"]["id"]

    # Get Album detail
    res = await client.get(f"/api/v1/albums/{album_id}")
    assert res.status_code == 200
    assert res.json()["data"]["title"] == "Discovery"


@pytest.mark.asyncio
async def test_song_upload_and_stream(client: AsyncClient, admin_token_headers: dict):
    # Create Artist
    res = await client.post(
        "/api/v1/artists",
        data={"name": "Test Artist"},
        headers=admin_token_headers,
    )
    artist_id = res.json()["data"]["id"]

    # Upload Song
    fake_mp3 = b"\xff\xfb\x90\xc4\x00\x00\x00\x00" * 200
    files = {"audio_file": ("test.mp3", fake_mp3, "audio/mpeg")}
    data = {"title": "One More Time", "artist_id": str(artist_id), "duration_seconds": "300"}

    res = await client.post(
        "/api/v1/songs/upload",
        data=data,
        files=files,
        headers=admin_token_headers,
    )
    assert res.status_code == 201
    song_id = res.json()["data"]["id"]

    # Stream Song (Full)
    res = await client.get(f"/api/v1/songs/{song_id}/stream")
    assert res.status_code == 200

    # Stream Song (Range Request)
    res = await client.get(f"/api/v1/songs/{song_id}/stream", headers={"Range": "bytes=0-100"})
    assert res.status_code == 206
    assert "Content-Range" in res.headers

    # Global Search
    res = await client.get("/api/v1/search?q=One")
    assert res.status_code == 200
    assert len(res.json()["data"]["songs"]) >= 1
