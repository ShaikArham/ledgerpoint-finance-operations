from decimal import Decimal
import pytest
from ledgerpoint.ledger import Entry, validate_journal

def test_balanced_journal():
    validate_journal([Entry('Bank', debit=Decimal('100.00')), Entry('Revenue', credit=Decimal('100.00'))])

def test_unbalanced_journal_rejected():
    with pytest.raises(ValueError, match='balanced'):
        validate_journal([Entry('Bank', debit=Decimal('99')), Entry('Revenue', credit=Decimal('100'))])

def test_negative_amount_rejected():
    with pytest.raises(ValueError, match='Invalid'):
        validate_journal([Entry('Bank', debit=Decimal('-1')), Entry('Revenue', credit=Decimal('1'))])

def test_fractional_cent_rejected():
    with pytest.raises(ValueError, match='decimal'):
        validate_journal([Entry('Bank', debit=Decimal('1.001')), Entry('Revenue', credit=Decimal('1.001'))])
