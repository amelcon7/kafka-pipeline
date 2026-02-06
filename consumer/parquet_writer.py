from pathlib import Path
from datetime import datetime

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


BASE_PATH = Path(__file__).resolve().parent / "lake" / "crm_events_parquet"


def write_event_parquet(event: dict):
    ts = datetime.fromisoformat(event["timestamp"])

    partition_path = (
        BASE_PATH
        / f"event_type={event['event_type']}"
        / f"year={ts.year}"
        / f"month={ts.month:02d}"
        / f"day={ts.day:02d}"
    )

    partition_path.mkdir(parents=True, exist_ok=True)

    file_path = partition_path / "events.parquet"

    df = pd.DataFrame([{
        "event_id": str(event["event_id"]),
        "event_type": event["event_type"],
        "source": event["source"],
        "timestamp": event["timestamp"],
        "account_id": event["payload"]["account_id"],
        "industry": event["payload"]["industry"],
        "region": event["payload"]["region"],
    }])

    table = pa.Table.from_pandas(df, preserve_index=False)

    if file_path.exists():
        pq.write_table(
            table,
            file_path,
            compression="snappy",
            use_dictionary=False,
            append=True,
        )
    else:
        pq.write_table(
            table,
            file_path,
            compression="snappy",
            use_dictionary=False,
        )
