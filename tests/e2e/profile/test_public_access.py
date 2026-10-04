"""Existing Profile data remains accessible without identity headers."""

import pytest
from sqlalchemy import text

from src.shared.database import sql_client
from .test_profiles import (
    create_certificate,
    create_company,
    create_education,
    create_experience,
    create_link,
    create_profile,
)


pytestmark = pytest.mark.asyncio


async def test_public_creations_share_one_anonymous_owner(client):
    company = await create_company(client)
    created = [
        await create_profile(client),
        await create_link(client),
        await create_experience(client, company["id"]),
        await create_education(client),
        await create_certificate(client),
    ]
    assert len({item["user_id"] for item in created}) == 1
    async with sql_client.get_session("read") as session:
        count = await session.scalar(
            text('SELECT count(*) FROM profile."User" WHERE is_anonymous')
        )
    assert count == 1


async def test_existing_profile_is_public(client):
    async with sql_client.get_session("read-write") as session:
        user_id = await session.scalar(
            text('INSERT INTO profile."User" (is_anonymous) VALUES (false) RETURNING id')
        )
        profile_id = await session.scalar(
            text('INSERT INTO profile."Profile" '
                 '(user_id, slug, full_name, title, bio) '
                 'VALUES (:user_id, :slug, :name, :title, :bio) RETURNING id'),
            {"user_id": user_id, "slug": "legacy-public", "name": "Legacy", "title": "Dev", "bio": "Bio"},
        )

    response = await client.get(f"/api/v1/profiles/{profile_id}")
    assert response.status_code == 200
    assert response.json()["user_id"] == user_id

    response = await client.put(
        f"/api/v1/profiles/{profile_id}",
        json={"title": "Public profile"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Public profile"

    response = await client.get("/api/v1/profiles/")
    assert response.status_code == 200
    assert any(item["id"] == profile_id for item in response.json())
