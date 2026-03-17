import re
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    ValidationError,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict
from models.transaction import *
from .insurance import *

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
    
class Address(SecureBaseModel):
    street: str = Field(min_length=1)
    city: str = Field(min_length=1)
    zip_code: str = Field(pattern=r"^\d{5}$")

    @field_validator("zip_code")
    @classmethod
    def zip_code_message(cls, v: str) -> str:
        if not re.fullmatch(r"^\d{5}$", v):
            raise ValueError("Zip Code must be exactly 5 digits.")
        return v

class Account(SecureBaseModel):
    user: User
    transactions: List[BankTransaction] = Field(default_factory=list)
    insurance_policy: Optional[InsurancePolicy] = None

    @computed_field
    @property
    def total_portfolio_value(self) -> Decimal:
        return sum((tx.amount for tx in self.transactions), Decimal("0"))

    @computed_field
    @property
    def risk_score(self) -> str:
        max_tx = max((tx.amount for tx in self.transactions), default=Decimal("0"))
        total = self.total_portfolio_value
        if max_tx >= Decimal("10000") or self.user.age < 21:
            return "High"
        if total >= Decimal("5000"):
            return "Medium"
        return "Low"
    
class User(SecureBaseModel):
    id: UUID | str
    user_first_name: str = Field(min_length=1)
    user_last_name: str = Field(min_length=1)
    email: EmailStr
    age: int = Field(ge=18, le=120)
    address: Address
    social_security_number: str = Field(min_length=4, exclude=True)  # auto-excluded

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: UUID | str) -> UUID | str:
        if isinstance(v, UUID):
            return v
        if isinstance(v, str):
            try:
                UUID(v)
                return v
            except ValueError:
                pass
            if re.fullmatch(r"ACC-\d{4}", v):
                return v
        raise ValueError("ID must be a valid UUID or match pattern ACC-XXXX.")

    @field_validator("age")
    @classmethod
    def validate_age_message(cls, v: int) -> int:
        if not (18 <= v <= 120):
            raise ValueError("Age must be between 18 and 120.")
        return v