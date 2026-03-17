import unittest
from datetime import date, datetime, timedelta
from decimal import Decimal
from pydantic import ValidationError

# Importing the models your friend built
from models.user import User, Address
from models.transaction import BankTransaction, Currency, TransactionType
from models.insurance import InsurancePolicy, PolicyStatus

class TestSecureGuardModels(unittest.TestCase):

    # --- USER MODEL TESTS ---
    def test_valid_user_creation(self):
        # The address must be a nested model with a 5-digit zip code [cite: 9]
        address = Address(street="123 Main St", city="Zgierz", zip_code="12345") 
        
        # Testing a valid User model [cite: 5]
        user = User(
            id="ACC-1234",                   # Must match regex ACC-XXXX [cite: 6]
            user_first_name="Jane",
            user_last_name="Doe",
            email="jane.doe@example.com",    # Valid email string [cite: 7]
            age=25,                          # Integer between 18 and 120 [cite: 8]
            address=address,
            social_security_number="000-11-2222"
        )
        self.assertEqual(user.age, 25)

    def test_user_age_validation(self):
        address = Address(street="123 Main St", city="Zgierz", zip_code="12345")
        
        # The system must catch ValidationErrors for invalid data [cite: 34]
        with self.assertRaises(ValidationError):
             # Age must be between 18 and 120 [cite: 8]
             User(
                 id="ACC-1234", 
                 user_first_name="Jane", 
                 user_last_name="Doe", 
                 email="jane@example.com", 
                 age=17, # Too young!
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
        # The social_security_number must be excluded when converted back to a dictionary [cite: 10]
        self.assertNotIn("social_security_number", data_dump) 

    # --- TRANSACTION MODEL TESTS ---
    def test_valid_transaction(self):
        # Testing the Transaction model [cite: 11]
        tx = BankTransaction(
            currency="USD",                  # 3-letter ISO code [cite: 12]
            amount=Decimal("150.50"),        # Decimal greater than 0 [cite: 13]
            timestamp=datetime.now(),        # Valid ISO datetime [cite: 14]
            transaction_type="CREDIT"        # DEBIT or CREDIT [cite: 15]
        )
        self.assertEqual(tx.currency, Currency.USD)
        self.assertEqual(tx.transaction_type, TransactionType.CREDIT)

    def test_transaction_negative_amount(self):
        # Amounts must be strictly greater than 0 [cite: 13]
        with self.assertRaises(ValidationError):
            BankTransaction(
                currency="EUR", 
                amount=Decimal("-50.00"),  # Invalid negative amount
                timestamp=datetime.now(), 
                transaction_type="DEBIT"
            )

    # --- INSURANCE POLICY TESTS ---
    def test_valid_insurance_policy(self):
        # Testing the InsurancePolicy model [cite: 16]
        start = date.today()
        end = start + timedelta(days=35) # End date must be at least 30 days after start_date [cite: 18]
        
        policy = InsurancePolicy(
            policy_number="POLNUM1234",  # Uppercase and exactly 10 characters [cite: 17]
            start_date=start,
            end_date=end,
            status=PolicyStatus.ACTIVE   # Enum of ACTIVE, ELAPSED, PENDING [cite: 19]
        )
        self.assertEqual(policy.policy_number, "POLNUM1234")

    def test_insurance_policy_date_logic(self):
        start = date.today()
        end = start + timedelta(days=10) 
        
        with self.assertRaises(ValidationError):
             # End date is only 10 days later, must fail the 30-day logic [cite: 18]
             InsurancePolicy(
                 policy_number="POLNUM1234", 
                 start_date=start, 
                 end_date=end, 
                 status="ACTIVE"
             )

if __name__ == '__main__':
    unittest.main()