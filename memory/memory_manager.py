import json
import os

MEMORY_FILE = "memory_store.json"


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)


def save_memory(memory_list):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory_list, f, indent=2)


def add_operational_memory(
    action_type,
    stress_level,
    confidence,
    summary
):
    memory_record = {
        "action_type": action_type,
        "stress_level": stress_level,
        "confidence": confidence,
        "summary": summary
    }


def retrieve_relevant_memories(action_type=None, limit=5):
    memories = load_memory()
    if action_type is None:
        return memories[-limit:]

    filtered = [
        m for m in memories
        if m["action"] == action_type
    ]
    return filtered[-limit:]