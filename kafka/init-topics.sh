#!/usr/bin/env bash
set -e

echo "Waiting for Kafka to be ready..."
cub kafka-ready -b kafka:29092 1 30

echo "Creating topic crm.events.raw"
kafka-topics \
  --bootstrap-server kafka:29092 \
  --create \
  --if-not-exists \
  --topic crm.events.raw \
  --partitions 1 \
  --replication-factor 1

echo "Topic list:"
kafka-topics --bootstrap-server kafka:29092 --list
