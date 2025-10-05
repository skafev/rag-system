import os
import json
from datetime import datetime, timedelta
import random

output_dir = "documents/json"
os.makedirs(output_dir, exist_ok=True)

categories = ["Electronics", "Books", "Clothing", "Home", "Sports"]
products = [
    "Laptop", "Headphones", "Smartphone", "Novel", "T-shirt",
    "Sneakers", "Coffee Maker", "Backpack", "Bicycle", "Watch"
]

# Generate 30 sample JSON files
for i in range(1, 31):
    timestamp = datetime.now() - timedelta(days=random.randint(0, 100))
    data = {
        "id": i,
        "name": random.choice(products),
        "category": random.choice(categories),
        "price": round(random.uniform(10, 500), 2),
        "in_stock": random.choice([True, False]),
        "created_at": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "description": f"This is a sample description for product #{i}. It demonstrates JSON structure."
    }

    file_path = os.path.join(output_dir, f"product_{i}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

print("30 JSON files generated in documents/json/")
