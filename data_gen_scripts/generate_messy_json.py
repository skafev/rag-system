import os
import json

output_dir = "documents/json"
os.makedirs(output_dir, exist_ok=True)
file_path = os.path.join(output_dir, "messy_json.json")

data = {
    "id": 999,
    "name": "   Messy Product   ",
    "category": "Electronics ",
    "price": "  123.45  ",
    "in_stock": " TRUE ",
    "created_at": "2023-09-01   12:00:00",
    "description": "   This JSON  has   extra   spaces   everywhere. ",
    "details": {
        "size": "  Medium ",
        "color": " Blue "
    }
}

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4)

print("Messy JSON generated at:", file_path)
