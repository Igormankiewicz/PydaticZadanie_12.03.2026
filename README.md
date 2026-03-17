# PydaticZadanie_12.03.2026
Grupa Genowefy Genowefy atakuje jeszcze raz!

Kamil Rochala oraz Igor Mankiewicz

# SecureGuard – Financial Data Validator

**SecureGuard** is a robust suite of Pydantic models designed to ingest, validate, and standardize "messy" raw financial data. It acts as a protective layer that ensures incoming data (JSON/Dicts) adheres to strict financial regulations and business logic before being processed further.

The system automatically handles data transformation (camelCase to snake_case), type coercion, and security-sensitive data exclusion.

---

## Getting Started

## Prerequisites

- Python 3.10+
    
- The following packages (defined in `requirements.txt`):
    
    - `pydantic`
        
    - `pydantic-settings`
        
    - `email-validator`
        

## Installation

1. **Clone the repository**:
    
    Bash
    
```
    git clone https://github.com/Igormankiewicz/PydaticZadanie_12.03.2026.git SecureGuard
    cd SecureGuard
```
    
2. **Set up a virtual environment**:
    
    Bash
    
```
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
```
    
3. **Install dependencies**:
    
    Bash
    
```
    pip install pydantic pydantic-settings email-validator
```
    

## Configuration

The application behavior is controlled via `GlobalConfig`. You can toggle between **STRICT** and **LAX** validation modes using the `VALIDATION_MODE` environment variable.

- **LAX (Default):** Allows flexible parsing (e.g., "123" as an integer).
    
- **STRICT:** Requires exact type matching.
    

---

## Model Architecture

## 1. User Model (`user.py`)

Represents individual identity and contact information.

- **`validate_id`**: Ensures the ID is either a valid UUID or follows the internal `ACC-XXXX` pattern.
    
- **`validate_age_message`**: Enforces an age range between 18 and 120 with a user-friendly error.
    
- **SSN Exclusion**: The `social_security_number` field is marked with `exclude=True`, ensuring it never appears in exported dictionaries or JSON files for security.
    

## 2. BankTransaction Model (`transaction.py`)

Handles individual financial movements.

- **`validate_currency_friendly`**: Normalizes currency input to uppercase and validates against allowed ISO codes (USD, EUR, GBP).
    
- **`coerce_amount`**: Manually handles string-to-Decimal conversion and enforces strictness rules if enabled.
    
- **`validate_amount_message`**: Ensures the transaction amount is strictly greater than 0.
    
- **`validate_tx_type_friendly`**: Normalizes and validates the transaction as either `DEBIT` or `CREDIT`.
    

## 3. InsurancePolicy Model (`insurance.py`)

Manages policy data and date-based business logic.

- **`validate_policy_number`**: Ensures the policy number is exactly 10 uppercase characters.
    
- **`validate_date_logic`**: A model-level validator that ensures the `end_date` is at least 30 days after the `start_date`.
    

## 4. Account Model (`user.py`)

A parent model that aggregates user data and transaction history.

- **`total_portfolio_value`**: A `@computed_field` that calculates the sum of all transaction amounts in the account.
    
- **`risk_score`**: A `@computed_field` that determines a "High," "Medium," or "Low" risk rating based on the user's age and the size of their transactions.
    

---

## Application Logic

## Data Transformation

The system uses a `SecureBaseModel` that automatically maps incoming **camelCase** JSON keys to Python **snake_case** attributes using an `alias_generator`.

## Error Handling (`main.py`)

Instead of crashing on invalid input, the `validate_account_payload` function catches `ValidationError` and returns a structured, user-friendly JSON report:

- **`loc`**: Pinpoints exactly where the error occurred (e.g., `address.zip_code`).
    
- **`msg`**: Provides a clear explanation of what went wrong.
