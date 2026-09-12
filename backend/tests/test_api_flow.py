def test_demo_flow(client):
    resp = client.post("/api/demo")
    assert resp.status_code == 200
    project = resp.json()
    project_id = project["id"]
    assert project["analysis_mode"] in ("ai", "local")

    commitments_resp = client.get(f"/api/projects/{project_id}/commitments")
    assert commitments_resp.status_code == 200
    commitments = commitments_resp.json()
    assert len(commitments) > 0

    waiting_resp = client.get(f"/api/projects/{project_id}/waiting")
    assert waiting_resp.status_code == 200
    assert len(waiting_resp.json()) > 0

    stats_resp = client.get(f"/api/projects/{project_id}/stats")
    assert stats_resp.status_code == 200
    stats = stats_resp.json()
    assert "risk_score" in stats

    forgotten_resp = client.get(f"/api/projects/{project_id}/forgotten")
    assert forgotten_resp.status_code == 200

    # complete a commitment and confirm stats update
    commitment_id = commitments[0]["id"]
    patch_resp = client.patch(f"/api/commitments/{commitment_id}", json={"status": "completed"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "completed"

    new_stats = client.get(f"/api/projects/{project_id}/stats").json()
    assert new_stats["completed"] >= 1


def test_analyze_empty_text_returns_400(client):
    resp = client.post("/api/analyze", data={"text": ""})
    assert resp.status_code == 400


def test_analyze_unsupported_file_returns_400(client):
    resp = client.post(
        "/api/analyze",
        files={"file": ("bad.exe", b"not a real file", "application/octet-stream")},
    )
    assert resp.status_code == 400


def test_delete_project(client):
    create = client.post("/api/projects", json={"name": "Temp project"})
    project_id = create.json()["id"]
    delete_resp = client.delete(f"/api/projects/{project_id}")
    assert delete_resp.status_code == 200
    get_resp = client.get(f"/api/projects/{project_id}")
    assert get_resp.status_code == 404
