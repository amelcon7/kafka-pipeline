import json
from confluent_kafka import Consumer
from psycopg2 import IntegrityError
from pydantic import ValidationError

from models import CRMEvent
from db import get_connection
from storage import write_event


TOPIC = "crm.events.raw"
BOOTSTRAP_SERVERS = "localhost:9092"
GROUP_ID = "crm-integration-consumer"


def build_consumer():
    return Consumer(
        {
            "bootstrap.servers": BOOTSTRAP_SERVERS,
            "group.id": GROUP_ID,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )


def process_event(event: CRMEvent):
    conn = get_connection()
    cur = conn.cursor()

    try:
        # Idempotency check
        cur.execute(
            "INSERT INTO processed_events (event_id) VALUES (%s)",
            (str(event.event_id),),
        )

        # Main persistence
        cur.execute(
            """
            INSERT INTO crm_account_events (
                event_id,
                event_type,
                source,
                event_timestamp,
                account_id,
                industry,
                region,
                raw_payload
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                str(event.event_id),
                event.event_type,
                event.source,
                event.timestamp,
                event.payload.account_id,
                event.payload.industry,
                event.payload.region,
                json.dumps(event.model_dump(mode="json")),
            ),
        )

        conn.commit()

        write_event(event.model_dump(mode="json"))

        return True

    except IntegrityError:
        # Duplicate event_id → replay
        conn.rollback()
        return True

    except Exception:
        conn.rollback()
        raise

    finally:
        cur.close()
        conn.close()


def main():
    consumer = build_consumer()
    consumer.subscribe([TOPIC])

    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print(f"Kafka error: {msg.error()}")
            continue

        try:
            payload = json.loads(msg.value())
            event = CRMEvent.model_validate(payload)

            process_event(event)
            consumer.commit(msg)

        except ValidationError as e:
            print("❌ Invalid event rejected:", e)
            consumer.commit(msg)

        except Exception as e:
            print("❌ Processing failed:", e)
            # no commit → retry on restart


if __name__ == "__main__":
    main()
