from __future__ import annotations

import uuid

from httpx import AsyncClient


async def test_list_leads_requires_auth(client: AsyncClient):
    resp = await client.get("/api/v1/leads")
    assert resp.status_code == 401


async def test_list_leads_success(
    client: AsyncClient, auth_headers: dict, sample_lead: dict
):
    resp = await client.get("/api/v1/leads", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] >= 1
    assert len(body["items"]) >= 1


async def test_get_lead_detail(
    client: AsyncClient, auth_headers: dict, sample_lead: dict
):
    lead_id = sample_lead["id"]
    resp = await client.get(f"/api/v1/leads/{lead_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["id"] == lead_id


async def test_get_lead_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = uuid.uuid4()
    resp = await client.get(f"/api/v1/leads/{fake_id}", headers=auth_headers)
    assert resp.status_code == 404


async def test_update_lead_status(
    client: AsyncClient, auth_headers: dict, sample_lead: dict
):
    lead_id = sample_lead["id"]
    resp = await client.patch(
        f"/api/v1/leads/{lead_id}/status",
        json={"status": "REACHED_OUT"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "REACHED_OUT"


async def test_update_lead_already_reached_out(
    client: AsyncClient, auth_headers: dict, sample_lead: dict
):
    lead_id = sample_lead["id"]
    # First update succeeds
    resp = await client.patch(
        f"/api/v1/leads/{lead_id}/status",
        json={"status": "REACHED_OUT"},
        headers=auth_headers,
    )
    assert resp.status_code == 200

    # Second update returns 409
    resp = await client.patch(
        f"/api/v1/leads/{lead_id}/status",
        json={"status": "REACHED_OUT"},
        headers=auth_headers,
    )
    assert resp.status_code == 409
