import json
from pathlib import Path


BASE_PATH = Path("lake/crm_events")


def write_event(event: dict):
    BASE_PATH.mkdir(parents=True, exist_ok=True)
    path = BASE_PATH / f"{event['event_id']}.json"

    with open(path, "w") as f:
        json.dump(event, f, indent=2)
