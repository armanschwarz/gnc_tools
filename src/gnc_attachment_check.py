#!/usr/bin/env python3

import argparse
import os
import urllib
from urllib import request

import util


def check_attachments(gnucash_file, base_path):
    session = util.open_book(gnucash_file)
    book = session.book

    file_paths = []
    file_metadata = []  # (path, date, description, accounts)

    for txn in util.get_all_transactions(book):
        link = txn.GetDocLink()
        if link:
            rel_path = request.url2pathname(urllib.parse.urlparse(link).path)
            # remove leading slashes as this breaks os.path.join
            while rel_path and rel_path[0] == '/':
                rel_path = rel_path[1:]
            path = os.path.join(base_path, rel_path)
            accounts = [util.get_long_name(s.GetAccount()) for s in txn.GetSplitList()]
            file_paths.append(path)
            file_metadata.append((path, txn.GetDate().date(), txn.GetDescription(), accounts))

    session.end()
    errors = [p for p in file_paths if not os.path.exists(p)]
    error_details = [m for m in file_metadata if not os.path.exists(m[0])]
    return errors, file_paths, error_details


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check whether all attached files are found"
    )
    parser.add_argument("gnucash_file")
    parser.add_argument("base_path")
    args = parser.parse_args()

    errors, file_paths, error_details = check_attachments(args.gnucash_file, args.base_path)

    print(
        "Found {} files to search in base path '{}'...".format(
            len(file_paths), args.base_path
        )
    )
    for path, date, description, accounts in error_details:
        print("Failed to find {}".format(path))
        print("  Date:        {}".format(date))
        print("  Description: {}".format(description))
        print("  Accounts:    {}".format(", ".join(accounts)))
    print("Found {} errors in {} files!".format(len(errors), len(file_paths)))
