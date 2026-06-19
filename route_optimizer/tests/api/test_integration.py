import pytest
from fastapi.testclient import TestClient
from route_optimizer.api.main import app
import os
from dotenv import load_dotenv

# Load env before client is created
load_dotenv()

client = TestClient(app)

def test_driver_crud():
    # 1. Create
    create_response = client.post("/api/v1/drivers/", json={
        "name": "Integration Test Driver",
        "phone": "555-1234",
        "status": "Available"
    })
    assert create_response.status_code == 201
    created_data = create_response.json()
    driver_id = created_data["id"]
    assert isinstance(driver_id, str)
    assert created_data["name"] == "Integration Test Driver"

    # 2. Read
    read_response = client.get(f"/api/v1/drivers/{driver_id}")
    assert read_response.status_code == 200
    assert read_response.json()["name"] == "Integration Test Driver"

    # 3. Update
    update_response = client.put(f"/api/v1/drivers/{driver_id}", json={
        "name": "Updated Driver",
        "phone": "555-1234",
        "status": "Busy"
    })
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Driver"
    assert update_response.json()["status"] == "Busy"

    # 4. Delete
    delete_response = client.delete(f"/api/v1/drivers/{driver_id}")
    assert delete_response.status_code == 204

    # 5. Verify Deletion
    verify_response = client.get(f"/api/v1/drivers/{driver_id}")
    assert verify_response.status_code == 404

def test_vehicle_crud():
    # 1. Create
    create_response = client.post("/api/v1/vehicles/", json={
        "name": "Integration Test Vehicle",
        "vehicleNumber": "TEST-123",
        "status": "Available"
    })
    assert create_response.status_code == 201
    vehicle_id = create_response.json()["id"]

    # 2. Read
    read_response = client.get(f"/api/v1/vehicles/{vehicle_id}")
    assert read_response.status_code == 200

    # 3. Delete
    client.delete(f"/api/v1/vehicles/{vehicle_id}")

def test_delivery_crud():
    # 1. Create
    create_response = client.post("/api/v1/deliveries/", json={
        "customerName": "Test Customer",
        "phoneNumber": "555-9999",
        "address": "123 Test St",
        "latitude": 28.5,
        "longitude": 77.1,
        "priority": "High",
        "status": "Pending",
        "packageWeight": 5.0
    })
    assert create_response.status_code == 201
    delivery_id = create_response.json()["id"]

    # 2. Read
    read_response = client.get(f"/api/v1/deliveries/{delivery_id}")
    assert read_response.status_code == 200
    assert read_response.json()["customerName"] == "Test Customer"

    # 3. Verify in Atlas via debug endpoint
    debug_response = client.get("/api/v1/debug/database")
    assert debug_response.status_code == 200
    debug_data = debug_response.json()
    assert debug_data["database"] == "logistics_db"
    assert debug_data["deliveries"] >= 1
    
    # 4. Delete
    client.delete(f"/api/v1/deliveries/{delivery_id}")

def test_health_endpoints():
    health_db = client.get("/api/v1/health/database")
    assert health_db.status_code == 200
    assert health_db.json()["status"] == "healthy"
    assert health_db.json()["database"] == "logistics_db"
    assert isinstance(health_db.json()["collections"], list)

if __name__ == "__main__":
    pytest.main([__file__])
