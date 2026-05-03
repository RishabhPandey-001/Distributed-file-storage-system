import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, "database", "metadata.json")


def read_db():
    if not os.path.exists(DB_FILE):
        return {"users": [], "files": []}

    with open(DB_FILE, "r") as f:
        try:
            data = json.load(f)
        except:
            return {"users": [], "files": []}

    if "users" not in data:
        data["users"] = []

    if "files" not in data:
        data["files"] = []

    return data


def write_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)