from datetime import date
from enum import Enum

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict

class ValidationMode(str, Enum):
    STRICT = "strict"
    LAX = "lax"

class GlobalConfig(BaseSettings):
    validation_mode: ValidationMode = ValidationMode.LAX
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

def get_strict_mode() -> bool:
    return GlobalConfig().validation_mode == ValidationMode.STRICT

class PolicyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ELAPSED = "ELAPSED"
    PENDING = "PENDING"

class SecureBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
        strict=get_strict_mode(),
)

# -- class --

class InsurancePolicy(SecureBaseModel):
    policy_number: str = Field(min_length=10, max_length=10)
    start_date: date
    end_date: date
    status: PolicyStatus

    @field_validator("policy_number")
    @classmethod
    def validate_policy_number(cls, v: str) -> str:
        if len(v) != 10 or not v.isupper():
            raise ValueError("Policy number must be uppercase and exactly 10 characters.")
        return v

    @model_validator(mode="after")
    def validate_date_logic(self) -> "InsurancePolicy":
        if self.end_date <= self.start_date:
            raise ValueError("Policy end_date must be after start_date.")
        if (self.end_date - self.start_date).days < 30:
            raise ValueError("Policy end_date must be at least 30 days after start_date.")
        return self