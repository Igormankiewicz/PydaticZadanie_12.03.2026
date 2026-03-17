from typing import Any, Dict, List

from pydantic import (
    ValidationError,
)

from models.insurance import *
from models.transaction import *
from models.user import *

def validate_account_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        account = Account.model_validate(payload)
        return {
            "ok": True,
            "data": account.model_dump(by_alias=True),  # SSN excluded automatically
        }

    except ValidationError as e:
        friendly_errors: List[Dict[str, str]] = []
        for err in e.errors():
            loc = ".".join(str(x) for x in err.get("loc", []))
            msg = err.get("msg", "Invalid value.")
            friendly_errors.append({"loc": loc, "msg": msg})

        return {
            "ok": False,
            "errors": friendly_errors,
        }

    except Exception as e:
        # fallback for unexpected runtime errors
        return {
            "ok": False,
            "errors": [{"loc": "system", "msg": f"Unexpected error: {str(e)}"}],
        }