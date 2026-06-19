from fastapi.testclient import TestClient
from route_optimizer.api.main import app

client = TestClient(app)

def test_crud_driver():
    # Create
    resp = client.post("/api/v1/drivers/", json={
        "name": "Test Driver",
        "phone": "123",
        "status": "Available"
    })
    assert resp.status_code == 201
    driver_id = resp.json()["id"]

    # Read
    resp = client.get(f"/api/v1/drivers/{driver_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Driver"

    # Delete
    resp = client.delete(f"/api/v1/drivers/{driver_id}")
    assert resp.status_code == 204
