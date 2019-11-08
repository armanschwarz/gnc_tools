# Usage

For help:

```
./gnc_assert.py --help
```

To run assertions to `2` decimal places with the GnuCash file located at `/path/to/account.gnucash`, and where assertions are written as transaction descriptions of the form `Balance Assertion: 123.45`:
```
./gnc_balance_assertion.py path/to/account.gnucash "(?<=Balance Assertion: )[\-]*\d*\.\d\d" 2
```