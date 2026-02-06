from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, StrictStr


class AccountCreatedPayload(BaseModel):
    account_id: StrictStr
    industry: StrictStr
    region: StrictStr


class CRMEvent(BaseModel):
    event_id: UUID
    event_type: Literal["account_created"]
    source: Literal["salesforce"]
    timestamp: datetime
    payload: AccountCreatedPayload

    class Config:
        extra = "forbid"
