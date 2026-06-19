import httpx
import json

base_url = "http://localhost:8000/api/v1/optimization"

modes = [
    ("distance", "distance_optimal"),
    ("duration", "distance_optimal"),  # duration optimal (using distance_optimal balancing mode logically, wait! no, balancing mode should be distance_optimal, opt mode should be duration. Wait. The user's prompt says: "DISTANCE_OPTIMAL: Focus on distance, balance distance. DURATION_OPTIMAL: Focus on duration, balance duration. BALANCED: balance both. STRICT: balance strict." 
    # Ah, the UI sends optimizationMode = 'distance'/'duration', and balancingMode = 'distance_optimal' / 'balanced' / 'strict'.
]

def test_optimization(vehicle_count, optimization_mode, balancing_mode):
    print(f"\n--- Testing {optimization_mode.upper()} + {balancing_mode.upper()} with {vehicle_count} vehicles ---")
    payload = {
        "vehicleCount": vehicle_count,
        "optimizationMode": optimization_mode,
        "balancingMode": balancing_mode
    }
    
    try:
        response = httpx.post(f"{base_url}/generate-routes", json=payload, timeout=30.0)
        data = response.json()
        
        if response.status_code != 200:
            print("Error:", data)
            return

        metrics = data.get("metrics", {})
        vehicles = metrics.get("vehicle_metrics", [])
        
        print(f"Total Distance: {metrics.get('total_distance')} km")
        print(f"Total Duration: {metrics.get('total_duration')} min")
        print(f"Distance StdDev: {metrics.get('distance_distribution_stddev')} km")
        print(f"Duration StdDev: {metrics.get('duration_distribution_stddev')} min")
        print(f"Stops StdDev: {metrics.get('stop_distribution_stddev')}")
        
        for v in vehicles:
            print(f"Vehicle: {v['vehicle_name']} | Stops: {v['num_stops']} | Distance: {v['distance']} km | Duration: {v['duration']} min")
            
    except Exception as e:
        print("Failed:", str(e))

# We need to run it against whatever the current state of DB deliveries are.
test_optimization(3, "distance", "distance_optimal")
test_optimization(3, "duration", "distance_optimal")
test_optimization(3, "distance", "balanced")
test_optimization(3, "distance", "strict")
