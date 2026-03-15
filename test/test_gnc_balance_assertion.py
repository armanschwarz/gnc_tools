import unittest
from pathlib import Path

from gnc_balance_assertion import gnc_balance_assertion


class TestGncTools(unittest.TestCase):

    def setUp(self):
        self.gnucash_file = str(Path(__file__).parent / "test_accounts.gnucash")
        self.assertion_amount_regex = r"(?<=Balance Assertion: )[\-]*\d*\.\d*"
        self.assertion_start_regex = r"(?<=\(since: )\d\d\d\d-\d\d-\d\d(?=\))"

    def test_balance_assertion_reports_failures(self):
        error_count, assertions_count, account_results = gnc_balance_assertion(
            self.gnucash_file,
            self.assertion_amount_regex,
            self.assertion_start_regex,
        )

        self.assertEqual(error_count, 1)
        self.assertEqual(assertions_count, 4)
        self.assertEqual(sorted(account_results), sorted([
            (
                "Root Account:Assets:Current Assets:Checking Account",
                1,
                ["\tERROR: Assertion of 123.6 against balance of 123.5 (1900-01-01 - 2026-03-16)"],
            ),
            ("Root Account:Assets:Current Assets:Savings Account", 1, []),
            ("Root Account:Assets:Current Assets:Cash in Wallet", 1, []),
            ("Root Account:Income:Other Income", 1, []),
        ]))
