# Kafka Event-Driven Integration Pipeline

## Overview

A disciplined, local Kafka pipeline demonstrating __enterprise-grade event ingestion, schema governance, idempotent processing, and analytics-ready outputs__ designed to complement a broader enterprise system.

This project intentionally focuses on correctness, replay safety, and integration reliability rather than scale or streaming analytics.

## Purpose

This pipeline demonstrates core skills:

* Event-driven architecture

* Explicit event contracts

* Schema validation

* Idempotent consumers

* Replay-safe processing

* Dual sinks:

    * __Postgres__ (audit / analytics)

    * __Parquet__ (data-lake style output)

Agents consume downstream outputs, not Kafka directly.

## Architecture Overview

### High-Level Flow
```yaml
CRM Event Producer
|
v
Kafka Topic: crm.events.raw
|
v
Integration Consumer
├── Schema validation (Pydantic)
├── Idempotency check
├── Transformation
|
├──> Postgres (audit + analytics)
└──> Parquet Lake (analytics-ready)
```

### Detailed Architecture Diagram
```
flowchart LR
A[CRM Producer<br/>Pydantic Validation] -->|Valid Events| B[Kafka Topic<br/>crm.events.raw]

B --> C[Integration Consumer]

C -->|Idempotency Check| D[(processed_events<br/>Postgres)]
C -->|Analytics Rows| E[(events table<br/>Postgres)]
C -->|Partitioned Output| F[Parquet Lake<br/>event_type / date]

C -.->|Invalid Events| X[Rejected Before Kafka]
```

* Producer rejects invalid events before Kafka
* Consumer is replay-safe and idempotent
* Parquet output is partitioned for analytics

## Event Contract

All events must conform to the following schema:
```
{
"event_id": "uuid",
"event_type": "account_created",
"source": "salesforce",
"timestamp": "ISO-8601",
"payload": {
"account_id": "001xx...",
"industry": "Healthcare",
"region": "US"
}
}
```

Schema validation is enforced using __Pydantic.__

## Idempotency & Replay Safety

* `event_id` is globally unique

* Consumer maintains a `processed_events` table

* Duplicate or replayed events are safely ignored

* Consumer can be restarted at any time

This enables:

* Safe Kafka replays

* Consumer restarts

* Disaster recovery testing

## Storage Layers

__Postgres (Audit & Analytics)__

* `processed_events` – deduplication / idempotency

* `events` – structured analytics table

__Parquet Data Lake__
```sql
Partitioned by:

event_type=account_created/
year=YYYY/
month=MM/
day=DD/
events-<event_id>.parquet
```

* Immutable files

* Analytics-ready

* Compatible with DuckDB / Spark / Trino


## Repository Structure
```
kafka-pipeline/
├── producer/
│   ├── send_test_events.py
│   └── producer.py
│
├── consumer/
│   ├── consumer.py
│   ├── models.py
│   ├── ddl.sql
│   ├── parquet_writer.py
│   └── lake/
│       └── .gitkeep
│
├── docker-compose.yml
├── .gitignore
└── README.md
```

## Running the Pipeline

__1. Start Kafka__
```
docker compose up -d
```

__2. Start the Consumer__
```
python consumer/consumer.py
```

__3. Send Test Events__
```
python producer/send_test_events.py
```


Expected behavior:

*  Invalid events rejected before Kafka

*  Valid events published

*  Consumer processes once

*  Replays do not duplicate data

## Replay Test

1. Stop the consumer

2. Restart the consumer

3. Re-send the same events

Result:

* No duplicate inserts

* Idempotency preserved

## Design Principles Demonstrated

* Explicit event contracts

* Schema-first ingestion

* Idempotent integration design

* Separation of transport and consumption

* Analytics-ready outputs

* Production-aligned Git hygiene

## Future Extensions

* Dead-letter queue (DLQ) Parquet sink

* Schema versioning

* DuckDB analytics queries

* Agent consumption layer

* Cloud object storage (S3-style)

## How This Fits a Larger System

This pipeline acts as a __reliable grounding layer__:

* Agents could consume validated, deduplicated data

* Kafka provides temporal decoupling

* Parquet enables batch analytics & memory retrieval

* Postgres enables auditing and traceability

## Summary

This project demonstrates how to build a small but correct event-driven integration pipeline — the kind used as foundational infrastructure in real enterprise systems.