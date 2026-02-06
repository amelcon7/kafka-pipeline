from datetime import datetime
from uuid import uuid4
from pydantic import ValidationError

from models import CRMEvent, AccountCreatedPayload
from producer import build_producer, publish_event

TOPIC = "crm.events.raw"
BOOTSTRAP_SERVERS = "localhost:9092"


def main():
    producer = build_producer(BOOTSTRAP_SERVERS)

    # ------------------
    # VALID EVENT
    # ------------------
    valid_event = CRMEvent(
        event_id=uuid4(),
        event_type="account_created",
        source="salesforce",
        timestamp=datetime.utcnow(),
        payload=AccountCreatedPayload(
            account_id="001xx000003NGsY",
            industry="Healthcare",
            region="US",
        ),
    )

    publish_event(
        producer=producer,
        topic=TOPIC,
        event=valid_event.model_dump(mode="json"),
        event_id=str(valid_event.event_id),
    )

    # ------------------
    # INVALID EVENT (INTENTIONAL)
    # ------------------
    try:
        CRMEvent(
            event_id=uuid4(),
            event_type="account_created",
            source="salesforce",
            timestamp=datetime.utcnow(),
            payload={
                "account_id": "001xx",
                "industry": "Healthcare",
                # region missing
            },
        )
    except ValidationError as e:
        print("\n❌ Invalid event rejected BEFORE Kafka:")
        print(e)

    producer.flush()


if __name__ == "__main__":
    main()
