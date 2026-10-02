import os, time
from dotenv import load_dotenv
from pymongo import MongoClient
import matplotlib.pyplot as plt

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["perf_lab"]
col = db["orders"]

FILTER = {"customer_id": 4242, "status": "delivered"}

def measure(label):
    res = db.command({
        "explain": {"find": "orders", "filter": FILTER, "sort": {"created_at": -1}},
        "verbosity": "executionStats",
    })
    stats = res["executionStats"]
    uses_index = "IXSCAN" in str(res["queryPlanner"]["winningPlan"])

    times = []
    for _ in range(20):
        t = time.perf_counter()
        list(col.find(FILTER).sort("created_at", -1))
        times.append((time.perf_counter() - t) * 1000)

    out = {
        "label": label,
        "docs_examined": stats["totalDocsExamined"],
        "server_ms": stats["executionTimeMillis"],
        "avg_client_ms": round(sum(times) / len(times), 2),
        "index_used": uses_index,
    }
    print(out)
    return out

print("Running BEFORE test (no index)... this may take a minute")
col.drop_indexes()
before = measure("No index")

print("Creating index...")
col.create_index(
    [("customer_id", 1), ("status", 1), ("created_at", -1)],
    name="cust_status_created",
)

print("Running AFTER test (with index)...")
after = measure("With compound index")

fig, ax = plt.subplots(1, 2, figsize=(10, 4))
labels = ["Before", "After"]
ax[0].bar(labels, [before["avg_client_ms"], after["avg_client_ms"]], color=["#d9534f", "#5cb85c"])
ax[0].set_title("Avg query time (ms)")
ax[1].bar(labels, [before["docs_examined"], after["docs_examined"]], color=["#d9534f", "#5cb85c"])
ax[1].set_title("Documents examined")
plt.tight_layout()
plt.savefig("benchmark_results.png", dpi=150)
print("Saved benchmark_results.png")