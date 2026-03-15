#!/usr/bin/python3

import os
from pathlib import Path

from gnucash import gnucash_core_c, Session, SessionOpenMode

_backends_loaded = False


def _find_backend_path():
    with open('/proc/self/maps') as f:
        for line in f:
            if 'libgnucash-guile' in line:
                return str(Path(line.split()[-1]).parent / 'gnucash')
    raise RuntimeError('Could not locate gnucash backend path via /proc/self/maps')


def open_book(gnucash_file):
    global _backends_loaded
    if not _backends_loaded:
        backend_path = _find_backend_path()
        gnucash_core_c.qof_load_backend_library(backend_path, 'libgncmod-backend-dbi.so')
        gnucash_core_c.qof_load_backend_library(backend_path, 'libgncmod-backend-xml.so')
        _backends_loaded = True

    with open(gnucash_file, 'rb') as f:
        header = f.read(16)

    if header.startswith(b'SQLite format 3'):
        uri = 'sqlite3://{}'.format(os.path.abspath(gnucash_file))
    else:
        uri = 'xml://{}'.format(os.path.abspath(gnucash_file))

    return Session(uri, SessionOpenMode.SESSION_READ_ONLY)


def guid_string(obj):
    return gnucash_core_c.guid_to_string(obj.GetGUID().instance)


def get_all_accounts(account, result=None):
    if result is None:
        result = []
    result.append(account)
    for child in account.get_children_sorted():
        get_all_accounts(child, result)
    return result


def get_all_transactions(book):
    seen = set()
    transactions = []
    for acct in get_all_accounts(book.get_root_account()):
        for split in acct.GetSplitList():
            t = split.parent
            guid = guid_string(t)
            if guid not in seen:
                seen.add(guid)
                transactions.append(t)
    return transactions


def get_long_name(account):
    parts = []
    while account is not None and account.GetName():
        parts.append(account.GetName())
        account = account.get_parent()
    return ':'.join(reversed(parts))
