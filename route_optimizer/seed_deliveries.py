from route_optimizer.database.repositories.delivery_repository import DeliveryRepository
import random

repo = DeliveryRepository()

# Delete existing
repo.collection.delete_many({})

base_lat = 28.4949
base_lon = 77.0895

from datetime import datetime, timezone

for i in range(20):
    repo.create({
        "customerName": f"Test Customer {i}",
        "phoneNumber": f"9999999{i:03d}",
        "address": f"Test Address {i}",
        "latitude": base_lat + random.uniform(-0.05, 0.05),
        "longitude": base_lon + random.uniform(-0.05, 0.05),
        "status": "Pending",
        "priority": "Medium",
        "packageWeight": 1.5,
        "createdAt": datetime.now(timezone.utc).isoformat()
    })

print("Seeded 20 deliveries.")
