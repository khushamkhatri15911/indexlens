import os
from dotenv import load_dotenv
from pymongo import MongoClient, ReadPreference

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))

# 1. Replica set info
info = client.admin.command("hello")
print("Replica set name:", info.get("setName"))
print("Primary node    :", info.get("primary"))
print("All nodes       :", info.get("hosts"))

# 2. Read from the primary (default)
col_primary = client["perf_lab"]["orders"]
cur = col_primary.find({"city": "Calgary"}).limit(5)
list(cur)
print("Normal read served by   :", cur.address)

# 3. Read from a secondary node
col_secondary = col_primary.with_options(
    read_preference=ReadPreference.SECONDARY_PREFERRED
)
cur = col_secondary.find({"city": "Calgary"}).limit(5)
list(cur)
print("Secondary-preferred read:", cur.address)