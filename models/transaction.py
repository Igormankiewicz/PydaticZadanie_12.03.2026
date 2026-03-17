from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)
from pydantic.alias_generators import to_camel
from pydantic_settings import BaseSettings, SettingsConfigDict

# global vars

class ValidationMode(str, Enum):
    STRICT = "strict"
    LAX = "lax"

class GlobalConfig(BaseSettings):
    validation_mode: ValidationMode = ValidationMode.LAX
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

def get_strict_mode() -> bool:
    return GlobalConfig().validation_mode == ValidationMode.STRICT

# enums

class PolicyStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ELAPSED = "ELAPSED"
    PENDING = "PENDING"

class Currency(str, Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class TransactionType(str, Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class SecureBaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="ignore",
        strict=get_strict_mode(),
)

class BankTransaction(SecureBaseModel):
    currency: Currency
    amount: Decimal = Field(gt=Decimal("0"))
    timestamp: datetime
    transaction_type: TransactionType

    @field_validator("currency", mode="before")
    @classmethod
    def validate_currency_friendly(cls, v: Any) -> Any:
        if isinstance(v, str):
            v = v.upper()
            if v not in {"USD", "EUR", "GBP"}:
                raise ValueError("Please select a valid currency: USD, EUR, or GBP.")
        return v

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_amount(cls, v: Any) -> Any:
        if isinstance(v, str):
            if get_strict_mode():
                raise ValueError("Amount must be a Decimal/number, not a string in strict mode.")
            try:
                return Decimal(v)
            except Exception:
                raise ValueError("Amount must be a valid positive number.")
        return v

    @field_validator("amount")
    @classmethod
    def validate_amount_message(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Transaction amount must be greater than 0.")
        return v

    @field_validator("transaction_type", mode="before")
    @classmethod
    def validate_tx_type_friendly(cls, v: Any) -> Any:
        if isinstance(v, str):
            v = v.upper()
            if v not in {"DEBIT", "CREDIT"}:
                raise ValueError("Transaction type must be either DEBIT or CREDIT.")
        return v