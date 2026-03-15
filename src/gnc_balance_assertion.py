#!/usr/bin/env python3

import argparse
import re
from math import log10

import pandas

import util


def gnc_balance_assertion(gnucash_file, assertion_amount_regex, assertion_start_regex=None):
    session = util.open_book(gnucash_file)
    book = session.book

    all_accounts = util.get_all_accounts(book.get_root_account())

    split_records = []    # rows for DataFrame: (date, amount, acct_guid, decimal_places)
    assertion_splits = []  # (acct_guid, assertion_amount, assertion_start, txn_date)

    for acct in all_accounts:
        acct_guid = util.guid_string(acct)
        for split in acct.GetSplitList():
            txn = split.parent
            amt = split.GetAmount()
            denom = amt.denom()
            dp = int(log10(denom)) if denom > 1 else 0
            amount = round(amt.num() / denom, dp)
            txn_date = txn.GetDate().replace(tzinfo=None)
            desc = txn.GetDescription() or ''

            split_records.append((txn_date, amount, acct_guid, dp))

            assertion_match = re.search('(' + assertion_amount_regex + ')', desc)
            if assertion_match:
                assertion_amount = float(assertion_match.group(0))
                assertion_start = pandas.to_datetime('1900-01-01')
                if assertion_start_regex is not None:
                    start_match = re.search('(' + assertion_start_regex + ')', desc)
                    if start_match:
                        assertion_start = pandas.to_datetime(start_match.group(0))
                assertion_splits.append((acct_guid, assertion_amount, assertion_start, txn_date))

    splits_df = pandas.DataFrame(split_records, columns=['Date', 'Amount', 'Account', 'DecimalPlaces'])

    error_count = 0
    assertions_count = 0
    account_results = []

    for acct in all_accounts:
        acct_guid = util.guid_string(acct)
        assertions = [(aa, as_, td) for (ag, aa, as_, td) in assertion_splits if ag == acct_guid]

        error_messages = []
        for assertion_amount, assertion_start, txn_date in assertions:
            subset = splits_df[
                (splits_df.Date <= txn_date)
                & (splits_df.Date >= assertion_start)
                & (splits_df.Account == acct_guid)
            ]
            balance = round(subset.Amount.sum(), int(subset.DecimalPlaces.max()))

            if abs(balance - assertion_amount) > 0:
                error_count += 1
                error_messages.append(
                    '\tERROR: Assertion of {} against balance of {} ({} - {})'.format(
                        assertion_amount,
                        balance,
                        assertion_start.date(),
                        txn_date.date(),
                    )
                )

        if assertions:
            assertions_count += len(assertions)
            account_results.append((util.get_long_name(acct), len(assertions), error_messages))

    session.end()
    return error_count, assertions_count, account_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Balance assertions for GnuCash")
    parser.add_argument("gnucash_file")
    parser.add_argument("--assertion_amount_regex")
    parser.add_argument("--assertion_start_regex", default=None)
    # parser.add_argument('-d', type=int, default=2, help='number of decimal places for comparison')
    args = parser.parse_args()

    print("parsing {}...".format(args.gnucash_file))
    error_count, assertions_count, account_results = gnc_balance_assertion(
        args.gnucash_file,
        args.assertion_amount_regex,
        args.assertion_start_regex,
    )
    for account_name, assertion_count, error_messages in account_results:
        print("Found {} assertions and {} errors in: {}".format(
            assertion_count, len(error_messages), account_name
        ))
        for msg in error_messages:
            print(msg)
    print("found {} errors in {} assertions!".format(error_count, assertions_count))
