from __future__ import annotations

from httpx import AsyncClient


async def test_submit_lead_success(client: AsyncClient, sample_resume_file):
    resp = await client.post(
        "/api/v1/leads",
        data={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
        },
        files={"resume": sample_resume_file},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["first_name"] == "Alice"
    assert body["last_name"] == "Smith"
    assert body["email"] == "alice@example.com"
    assert body["status"] == "PENDING"
    assert body["resume_url"].startswith("/uploads/")
    assert body["resume_url"].endswith(".pdf")


async def test_submit_lead_missing_fields(client: AsyncClient, sample_resume_file):
    resp = await client.post(
        "/api/v1/leads",
        data={"first_name": "Alice"},  # missing last_name and email
        files={"resume": sample_resume_file},
    )
    assert resp.status_code == 422


async def test_submit_lead_invalid_email(client: AsyncClient, sample_resume_file):
    resp = await client.post(
        "/api/v1/leads",
        data={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "not-an-email",
        },
        files={"resume": sample_resume_file},
    )
    assert resp.status_code == 422


async def test_submit_lead_invalid_file_type(client: AsyncClient):
    resp = await client.post(
        "/api/v1/leads",
        data={
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice@example.com",
        },
        files={"resume": ("notes.txt", b"some text", "text/plain")},
    )
    assert resp.status_code == 422
    assert "Invalid file type" in resp.json()["detail"]
