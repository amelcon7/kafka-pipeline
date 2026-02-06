import json
from confluent_kafka import Producer


def delivery_report(err, msg):
    if err is not None:
        print(f"❌ Delivery failed: {err}")
    else:
        print(
            f"✅ Delivered event_id={msg.key().decode()} "
            f"to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}"
        )


def build_producer(bootstrap_servers: str) -> Producer:
    return Producer(
        {
            "bootstrap.servers": bootstrap_servers,
            "acks": "all",
            "enable.idempotence": True,
            "linger.ms": 10,
        }
    )


def publish_event(
    producer: Producer,
    topic: str,
    event: dict,
    event_id: str,
):
    producer.produce(
        topic=topic,
        key=event_id.encode(),
        value=json.dumps(event).encode(),
        on_delivery=delivery_report,
    )
    producer.poll(0)
