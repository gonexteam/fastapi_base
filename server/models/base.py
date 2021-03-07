from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Schema, BaseConfig, Field


class RWModel(BaseModel):
    class Config(BaseConfig):
        allow_population_by_alias = True
        json_encoders = {
            datetime: lambda dt: dt.replace(tzinfo=timezone.utc)
                .isoformat()
                .replace("+00:00", "Z")
        }


class DateTimeModelMixin(BaseModel):
    created_at: Optional[datetime] = Field(..., alias="createdAt", default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(..., alias="updatedAt", default_factory=datetime.utcnow)
