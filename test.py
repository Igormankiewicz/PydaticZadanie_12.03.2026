import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError

from models.user import User, Address
from models.transaction import BankTransaction, Currency, TransactionType
from models.insurance import InsurancePolicy, PolicyStatus

class TestSecureGuardModels(unittest.TestCase):

    def test_valid_user_creation(self):
        address = Address(street="123 Main St", city="Zgierz", zip_code="12345") 
        
        user = User(
            id="ACC-1234",
            user_first_name="Jane",
            user_last_name="Doe",
            email="jane.doe@example.com",
            age=25,
            address=address,
            social_security_number="000-11-2222"
        )
        self.assertEqual(user.age, 25)

    def test_user_age_validation(self):
        address = Address(street="123 Main St", city="Zgierz", zip_code="12345")
        
        with self.assertRaises(ValidationError):
             User(
                 id="ACC-1234", 
                 user_first_name="Jane", 
                 user_last_name="Doe", 
                 email="jane@example.com", 
                 age=17,
                 address=address, 
                 social_security_number="000-11-2222"
             )

    def test_user_ssn_exclusion(self):
        address = Address(street="123 Main St", city="Zgierz", zip_code="12345")
        user = User(
            id="ACC-1234", user_first_name="Jane", user_last_name="Doe", 
            email="jane@example.com", age=30, address=address, social_security_number="000-11-2222"
        )
        
        data_dump = user.model_dump()
        self.assertNotIn("social_security_number", data_dump) 

    def test_valid_transaction(self):
        tx = BankTransaction(
            currency="USD",
            amount=Decimal("150.50"),
            timestamp=datetime.now(),
            transaction_type="CREDIT"
        )
        self.assertEqual(tx.currency, Currency.USD)
        self.assertEqual(tx.transaction_type, TransactionType.CREDIT)

    def test_transaction_negative_amount(self):
        with self.assertRaises(ValidationError):
            BankTransaction(
                currency="EUR", 
                amount=Decimal("-50.00"),
                timestamp=datetime.now(), 
                transaction_type="DEBIT"
            )

    def test_valid_insurance_policy(self):
        start = date.today()
        end = start + timedelta(days=35)
        
        policy = InsurancePolicy(
            policy_number="POLNUM1234",
            start_date=start,
            end_date=end,
            status=PolicyStatus.ACTIVE
        )
        self.assertEqual(policy.policy_number, "POLNUM1234")

    def test_insurance_policy_date_logic(self):
        start = date.today()
        end = start + timedelta(days=10) 
        
        with self.assertRaises(ValidationError):
             InsurancePolicy(
                 policy_number="POLNUM1234", 
                 start_date=start, 
                 end_date=end, 
                 status="ACTIVE"
             )

if __name__ == '__main__':
    unittest.main()