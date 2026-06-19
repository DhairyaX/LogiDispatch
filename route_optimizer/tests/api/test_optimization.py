from fastapi.testclient import TestClient
from route_optimizer.api.main import app

client = TestClient(app)

def test_simulate_day_and_optimize():
    # Simulate day
    resp = client.post("/api/v1/optimization/simulate-day")
    assert resp.status_code == 200

    # Test optimization
    resp = client.post("/api/v1/optimization/generate-routes", json={
        "vehicleCount": 3,
        "optimizationMode": "distance",
        "balancingMode": "balanced"
    })
    
    assert resp.status_code == 200
    data = resp.json()
    assert "routes" in data
    assert data["vehiclesUsed"] > 0
    
    # Test analytics
    resp = client.get("/api/v1/analytics/fleet")
    assert resp.status_code == 200
    data = resp.json()
    assert "fleetUtilization" in data
