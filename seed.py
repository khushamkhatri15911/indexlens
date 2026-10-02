import os, random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
col = MongoClient(os.getenv("MONGODB_URI"))["perf_lab"]["orders"]
col.drop()

cities = ["Calgary", "Toronto", "Vancouver", "Mumbai", "Delhi", "London"]
statuses = ["pending", "shipped", "delivered", "cancelled"]
start = datetime(2024, 1, 1)

batch = []
for i in range(200_000):
    batch.append({
        "order_id": i,
        "customer_id": random.randint(1, 20_000),
        "city": random.choice(cities),
        "status": random.choice(statuses),
        "amount": round(random.uniform(5, 500), 2),
        "created_at": start + timedelta(minutes=random.randint(0, 600_000)),
    })
    if len(batch) == 10_000:
        col.insert_many(batch)
        print("Inserted so far:", i + 1)
        batch = []

print("Done! Total documents:", col.count_documents({}))